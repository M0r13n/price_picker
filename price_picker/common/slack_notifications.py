import json
import requests as r
from flask import current_app as app
import logging


def send_after(action: callable):
    def decorator_func(func):
        def wrapper_func(*args, **kwargs):
            response, status_code = func(*args, **kwargs)
            # on success
            if 200 <= status_code < 300:
                action()

            return response, status_code

        return wrapper_func

    return decorator_func


def send_login_notice():
    url = app.config.get('SLACK_WEBHOOK')
    text = "Erfolgreicher Login auf dem Pricepicker!"
    if url:
        data = json.dumps({'text': text})
        resp = r.post(url, data=data)
        return resp.status_code
    return None


def send_login_failed_notice(user):
    url = app.config.get('SLACK_WEBHOOK')
    text = f"Fehlgeschlagender Login Versuch für Nutzer: {user}!"
    logging.error(text)
    if url:
        data = json.dumps({'text': text})
        resp = r.post(url, data=data)
        return resp.status_code
    return None


def send_cash_notification():
    url = app.config.get('SLACK_WEBHOOK')
    text = "Du hast gerade 1€ verdient!"
    if url:
        data = json.dumps({'text': text})
        resp = r.post(url, data=data)
        return resp.status_code
    return None
