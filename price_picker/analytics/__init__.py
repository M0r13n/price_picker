"""
Super simple Analytics extension to track basic user interactions inside a Flask app.

This extension is biased and expects you to use Sqlalchemy to store records.

NOTE: This extension stores every interaction in a separate database column. This is
not ideal for larger applications with lots of page visits.
"""
import datetime as dt
import json
from flask import _request_ctx_stack, g, request
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData, select, desc


class AnalyticsRecord(object):
    """
    Class to store all data
    """

    def __init__(self, url='/', user_agent=None, view_args='', status_code=200, path='/', latency=0,
                 timestamp=dt.datetime.utcnow(), content_length=0, request=None, url_args=None, ua_browser=None,
                 ua_platform=None, ua_language=None, ua_version=None, referer='-'):
        self.url = url
        self.user_agent = user_agent
        self.view_args = view_args
        self.status_code = status_code
        self.path = path
        self.latency = latency
        self.timestamp = timestamp
        self.content_length = content_length
        self.request = request
        self.url_args = url_args
        self.ua_browser = ua_browser
        self.ua_platform = ua_platform
        self.ua_language = ua_language
        self.ua_version = ua_version
        self.referer = referer

    def __repr__(self):
        return f"<RequestRecord:: Timestamp:{self.timestamp} | Path:{self.path} | Status:{self.status_code} | User_Agent:{self.user_agent}>"


class Analytics(object):
    """
    Analytics App
    """

    def __init__(self, app=None, db=None, blueprints=None):
        """
        Create a new instance of the analyzer.
        :param app: The Flask App instance
        :param db: A Sqlalchemy instance, e.g. db = Sqlalchemy(app)
        :param blueprints:  A whitelist for blueprints that should be tracked.
                            If this attribute is set only views whose blueprint name matches any of the names inside the
                            blueprints list will be tracked. To track all requests set this attribute to None.
                            Example whitelist could be: blueprints = ['main', 'admin'].
        """
        self.app = None
        self.db = None
        self.table = None
        self.metadata = None
        self.table_name = 'analytics_data'
        self.engine = None
        self.blueprints = None
        if app and db:
            self.init_app(app, db, blueprints)

    def init_app(self, app, db, blueprints=None):
        """
        Initializes an existing instance. Useful when using the application factory pattern.
        :param app: The Flask App instance
        :param db: A Sqlalchemy instance, e.g. db = Sqlalchemy(app)
        :param blueprints:  A whitelist for blueprints that should be tracked.
                            If this attribute is set only views whose blueprint name matches any of the names inside the
                            blueprints list will be tracked. To track all requests set this attribute to None.
                            Example whitelist could be: blueprints = ['main', 'admin'].
        """
        if not app or not db:
            raise ValueError("Flask App instance and sqlalchemy db object are required")
        self.app = app
        self.db = db

        self.blueprints = blueprints

        # check if table exists on first startup
        # NOTE: The table cannot be altered yet.
        # So when you change the table layout it might be incompatible with an existing table.
        # TODO come up with a nice idea on how make the table changeable

        with self.app.app_context():
            self.engine = db.engine
            self.metadata = MetaData(db.engine)
            if not self.engine.dialect.has_table(self.engine, self.table_name):
                self.table = Table(
                    self.table_name,
                    self.metadata,
                    Column('id', Integer, primary_key=True),
                    Column('url', String(128)),
                    Column('user_agent', String(256)),
                    Column('view_args', String(128)),
                    Column('status_code', Integer),
                    Column('path', String(64)),
                    Column('latency', Float),
                    Column('timestamp', DateTime),
                    Column('request', String(64)),
                    Column('url_args', String(64)),
                    Column('ua_browser', String(16)),
                    Column('ua_language', String(16)),
                    Column('ua_platform', String(16)),
                    Column('ua_version', String(16)),
                    Column('referer', String(64))
                )
                # Create the table if it does not exist
                self.table.create(bind=self.engine)
            else:
                self.metadata.reflect(bind=self.engine)
                self.table = self.metadata.tables[self.table_name]

        # register event hooks
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def store_record(self, record: AnalyticsRecord):
        """
        Store a record to the database.
        """
        with self.engine.begin() as conn:
            stmt = self.table.insert().values(
                url=str(record.url)[:128],
                ua_browser=str(getattr(record.user_agent, 'browser', '-'))[:16],
                ua_language=str(getattr(record.user_agent, 'language', '-'))[:16],
                ua_platform=str(getattr(record.user_agent, 'platform', '-'))[:16],
                ua_version=str(getattr(record.user_agent, 'version', '-'))[:16],
                user_agent=str(record.user_agent),
                view_args=json.dumps(record.view_args)[:64],
                status_code=record.status_code,
                path=str(record.path)[:64],
                latency=record.latency,
                request=str(record.request)[:64],
                timestamp=record.timestamp,
                referer=str(record.referer)[:64]
            )
            conn.execute(stmt)

    def query(self, from_=None, until=None):
        """
        Query the analytics table. By using db.session.query(...) it is possible to use the built in pagination!
        :param from_: datetime.datetime object specifying the earliest date that should be included
        :param until: datetime.datetime object specifying the latest date that should be included
        :return: BaseQuery
        """
        if from_ is None:
            from_ = dt.datetime.utcnow()
        if until is None:
            until = dt.datetime(1970, 1, 1)

        return self.db.session.query(self.table).filter(self.table.c.timestamp.between(until, from_)).order_by(
            self.table.c.timestamp.desc())

    def _drop_db(self):
        """
        Drops the database
        :return:
        """
        self.table.drop(checkfirst=True)

    def before_request(self):
        """ Only used to store the time when a request is first issued to be able to measure latency"""
        g.start_time = dt.datetime.utcnow()

    def after_request(self, response):
        """
        Store all information about the request
        :param response: pass the response object without touching it
        :return: original Flask response
        """
        ctx = _request_ctx_stack.top

        if self.blueprints:
            print(ctx.request.blueprint)
            if ctx.request.blueprint not in self.blueprints:
                return response

        t_0 = getattr(g, 'start_time', dt.datetime.utcnow())
        record = AnalyticsRecord(url=ctx.request.url,
                                 user_agent=ctx.request.user_agent,
                                 view_args=ctx.request.view_args,
                                 status_code=response.status_code,
                                 path=ctx.request.path,
                                 latency=(dt.datetime.utcnow() - t_0).microseconds // 100000,
                                 timestamp=t_0,
                                 content_length=response.content_length,
                                 request=f"{ctx.request.method}{ctx.request.url}{ctx.request.environ.get('SERVER_PROTOCOL')}",
                                 url_args=dict([(k, ctx.request.args[k]) for k in ctx.request.args]),
                                 referer=request.headers.get("Referer")
                                 )

        self.store_record(record)
        return response
