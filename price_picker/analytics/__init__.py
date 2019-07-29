import uuid
import json
import datetime as dt
from redis import Redis
from flask import session, g, request
from math import ceil

SORTED_SESSION_LIST = 'sessions'
SESSIONS = 'session:'

SORTED_VISIT_LIST = 'visits'
VISITS = 'visit:'

TOP_LIST = 'top_list'


def first_or_none(result):
    if result and len(result) > 0:
        return result[0]
    return None


class Analytics(object):
    """
    Analytics App
    """

    def __init__(self, app=None, redis_url=None, blueprints=None, max_entries=1e6):
        """
        Create a new instance
        :param app: Flask App instance
        :param redis_url: Connection to redis server (e.g. redis://localhost:6379/0/)
        :param blueprints: If provided only requests whose blueprint name matches any of the names inside this list are tracked
        """
        self.app = None
        self.redis = Redis()
        self.blueprints = None
        self.max_entries = max_entries
        self.last_clean_up = 0

        if app:
            self.init_app(app, redis_url, blueprints, max_entries)

    def init_app(self, app, redis_url, blueprints=None, max_entries=1e6):
        """
        Actual initialization of the instance.
        :param app: Flask App instance
        :param redis_url: Connection to redis server (e.g. redis://localhost:6379/0/)
        :param blueprints: If provided only requests whose blueprint name matches any of the names inside this list are tracked
        :return:
        """
        if not app:
            raise ValueError("Flask App instance required")

        self.app = app
        self.blueprints = blueprints
        self.redis = Redis.from_url(redis_url)
        self.max_entries = max_entries

        # register event hooks
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """
        Executed before a request is processed.
        Used to add new sessions to db.
        """
        g.start_time = dt.datetime.now()
        if 'UUID' not in session.keys() or not self.redis.zrank(SORTED_SESSION_LIST, session['UUID']):
            _uuid = session.get('UUID', default=uuid.uuid4())
            session['UUID'] = _uuid
            s = dict(
                user_agent=request.user_agent.string,
                ua_browser=request.user_agent.browser,
                ua_language=request.user_agent.language,
                ua_platform=request.user_agent.platform,
                ua_version=request.user_agent.version,
            )
            self.store_session(_uuid, s)

    def after_request(self, response):
        """
        Executed after a request is processed.
        Used to store page visits
        """
        # only track data for specified blueprints
        if self.blueprints:
            if request.blueprint not in self.blueprints:
                return response

        t_0 = getattr(g, 'start_time', dt.datetime.now())

        visit = dict(
            session_id=session.get('UUID', 0),
            timestamp=dt.datetime.now().timestamp(),
            url=request.url,
            view_args=request.view_args,
            status_code=response.status_code,
            path=request.path,
            latency=(dt.datetime.now() - t_0).microseconds / 100000,
            content_length=response.content_length,
            referer=request.referrer,
            values=request.values
        )
        self.store_visit(visit)
        self.update_top_list(request.path)
        return response

    def clean_up(self):
        # limit session cleaning to every 5 secs
        if dt.datetime.now().timestamp() - 5 <= self.last_clean_up:
            # Redis is able to delete 10,000 tokens per second across a network, and over 60,000 tokens per second locally.
            # Let´s say we have 500k users per day, then after two days the limit of 1m unique session records is reached.
            # Which means from there on we will delete sessions periodically.
            # A day has 86.400 seconds, so we have ~6 users per second (500.000 / 86.400)
            # So there is a total of ~30 tokens every 5 seconds to be deleted. Which es waaay beyond 10.000 tokens / second.
            return

        for i, j in [(SORTED_SESSION_LIST, SESSIONS), (SORTED_VISIT_LIST, VISITS)]:
            size = self.redis.zcard(i)
            if size > self.max_entries:
                last = size - self.max_entries
                tokens = self.redis.zrange(i, 0, last - 1)
                # remove tokens
                self.redis.zrem(i, *tokens)
                self.redis.hdel(j, *tokens)

        self.last_clean_up = dt.datetime.now().timestamp()

    def update_top_list(self, path):
        score = self.redis.zscore(TOP_LIST, path) or 0
        self.redis.zadd(TOP_LIST, {path: score - 1})

    def store_session(self, _uuid, s):
        # store session id in list
        self.redis.zadd(SORTED_SESSION_LIST, {_uuid: dt.datetime.now().timestamp()})
        # store full session
        self.redis.hset(SESSIONS, _uuid, json.dumps(s))
        # cleanup
        self.clean_up()

    def store_visit(self, visit):
        # increment event id
        _id = self.redis.incr('visit_counter')
        # store event in sorted list
        self.redis.zadd(SORTED_VISIT_LIST, {_id: dt.datetime.now().timestamp()})
        # store full event
        self.redis.hset(VISITS, _id, json.dumps(visit))
        # cleanup
        self.clean_up()

    def get_visits_paginated(self, page=1, limit=15):
        page = max(page, 1)
        keys = self.redis.zrevrange(SORTED_VISIT_LIST, (page - 1) * limit, page * limit - 1)
        results = []
        total = self.redis.zcard(SORTED_VISIT_LIST)
        try:
            if keys:
                visits = [json.loads(x) for x in self.redis.hmget(VISITS, keys)]
                for visit in visits:
                    session_key = visit.get('session_id', '')
                    sess = self.redis.hget(SESSIONS, session_key)

                    # skip results without corresponding session
                    if sess:
                        results.append({**visit, **json.loads(sess)})
        except Exception as e:
            self.app.logger.error(e)
        return FakePagination(self.get_visits_paginated, page, limit, total, results)


class FakePagination(object):
    """
    1-to-1 of Pagination from sqlalchemy
    So its possible to use existing pagination macros without ANY changes etc.
    """

    def __init__(self, method, page, per_page, total, items):
        self.method = method
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self):
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        return self.method(self.page - 1, self.per_page)

    @property
    def prev_num(self):
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        return self.page > 1

    def next(self, error_out=False):
        return self.method(self.page + 1, self.per_page)

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_num(self):
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):

        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.page - left_current - 1 and
                     num < self.page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
