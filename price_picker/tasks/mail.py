from price_picker import celery, mail
from flask_mail import Message
from flask import current_app, render_template
from price_picker.models import Preferences


@celery.task
def async_test_email():
    """ this works only after settings were updated"""
    p = Preferences.query.first()
    if p is None:
        current_app.logger.warning('No Preferences could be found. Abort.')
        return
    msg = Message("Hello",
                  sender="Test vom Price-Picker!",
                  recipients=[p.mail_config['MAIL_USERNAME']])
    current_app.config.update(p.mail_config)
    mail.app = current_app
    mail.state = mail.init_app(current_app)
    with current_app.app_context():
        mail.send(msg)


@celery.task
def async_send_confirmation_mail(email=None):
    p = Preferences.query.first()
    if p is None:
        current_app.logger.warning('No Preferences could be found. Abort.')
        return
    if email is None:
        current_app.logger.warning('Email is None. Abort.')
        return
    current_app.config.update(p.mail_config)
    mail.app = current_app
    mail.state = mail.init_app(current_app)
    template = 'email/confirmation'
    with current_app.app_context():
        msg = Message("Bestätigung Kundenanfrage",
                      sender="Test vom Price-Picker!",
                      recipients=[email])
        msg.body = render_template(template + '.txt')
        mail.send(msg)
