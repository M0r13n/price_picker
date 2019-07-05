from price_picker import celery, Mail
from flask_mail import Message
from flask import current_app, render_template
from price_picker.models import Preferences, Enquiry


@celery.task
def async_test_email():
    """ this works only after settings were updated"""
    p = Preferences.query.first()
    if p is None:
        current_app.logger.warning('No Preferences could be found. Abort.')
        return
    msg = Message("Hello",
                  sender=p.mail_config['MAIL_DEFAULT_SENDER'],
                  recipients=[p.mail_config['MAIL_USERNAME']])
    current_app.config.update(p.mail_config)
    mail = Mail(current_app)
    with current_app.app_context():
        mail.send(msg)


@celery.task
def async_send_confirmation_mail(email=None, enquiry_id=None):
    p = Preferences.query.first()
    if p is None:
        current_app.logger.warning('No Preferences could be found. Abort.')
        return
    if email is None:
        current_app.logger.warning('Email is None. Abort.')
        return

    current_app.config.update(p.mail_config)
    mail = Mail(current_app)

    template = 'email/confirmation'
    with current_app.app_context():
        msg = Message("Bestätigung Kundenanfrage",
                      sender=p.mail_config['MAIL_DEFAULT_SENDER'],
                      recipients=[email])
        msg.body = render_template(template + '.txt')
        mail.send(msg)
        if enquiry_id is not None and p.order_copy_mail_address is not None:
            enquiry = Enquiry.query.get(enquiry_id)
            msg = Message("Neue Kundenanfrage über den Price-Picker",
                          sender=p.mail_default_sender,
                          recipients=[p.order_copy_mail_address])

            template = 'email/new_enquiry'
            msg.body = render_template(template + '.txt', enquiry=enquiry)
            mail.send(msg)
