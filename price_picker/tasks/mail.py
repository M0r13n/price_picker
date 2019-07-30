from price_picker import celery
from price_picker.models import Preferences
from flask import current_app, render_template
from flask_mail import Mail, Message
from celery.exceptions import MaxRetriesExceededError, Retry
from price_picker.common.constants import CELERY_TASK_ZSET, MAX_TRIES, DELAYS
from price_picker.common.util import now


def single_to_list(recipients):
    """ Ensure recipients are always passed as a list """
    if isinstance(recipients, str):
        return [recipients]
    return recipients


def configured_confirmation_recipient():
    p = Preferences.query.first()
    if p is None:
        return None
    return p.order_copy_mail_address


def default_mail_sender():
    p = Preferences.query.first()
    if p is None:
        return None
    return p.mail_default_sender or p.mail_username


class BaseEmail:
    def __init__(self, subject: str = None, text_body: str = None, html_body: str = None, sender: str = None, recipients: [] = None):
        self.subject = subject
        self.text_body = text_body
        self.html_body = html_body
        self.sender = sender
        self.recipients = single_to_list(recipients)

    def to_msg(self) -> Message:
        msg = Message(self.subject, sender=self.sender, recipients=self.recipients)
        msg.body = self.text_body
        msg.html = self.html_body
        return msg


class CustomerConfirmationEmail(BaseEmail):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject = "Bestätigung Kundenanfrage"
        tpl = 'email/confirmation'
        self.text_body = render_template(tpl + '.txt')


class EnquiryReceivedEmail(BaseEmail):
    def __init__(self, enquiry, **kwargs):
        super().__init__(**kwargs)
        self.subject = "Neue Kundenanfrage über den Price-Picker"
        tpl = 'email/new_enquiry'
        self.text_body = render_template(tpl + '.txt', enquiry=enquiry)


class TestEmail(BaseEmail):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject = "Test Anfrage über den Price-Picker"
        self.text_body = "Dies ist eine Testmail! :-)"


@celery.task(name='send_email', bind=True, max_retries=None)
def send_email_task(task, email):
    current_app.logger.info(f'Sending email with {task.request.retries} retries')
    attempt = task.request.retries + 1

    # update state
    task.update_state(state='PROGRESS', meta={'retries': attempt, 'max_retries': MAX_TRIES})

    # send mail and retry with exponential retries timeouts
    try:
        do_send_email(email)
    except Exception as exc:
        delay = DELAYS[task.request.retries]
        try:
            task.retry(countdown=delay, max_retries=(MAX_TRIES - 1))
        except MaxRetriesExceededError:
            current_app.logger.error(f'Could not send email {email["subject"]} to {email["recipients"]}. '
                                     f'Tried it {MAX_TRIES} times. Giving up now. Reason was : {str(exc)}')
            task.update_state(state='FAILED', meta={'retries': attempt, 'max_retries': MAX_TRIES})
        except Retry:
            current_app.logger.warning(f'Could not send email. Tried it {attempt} times. Retrying it in {delay} seconds.')
            raise
    else:
        current_app.logger.info('Email sent successfully')


def do_send_email(email):
    p = Preferences.query.first()
    if p is None:
        current_app.logger.warning('No Preferences could be found. Abort.')
        return
    current_app.config.update(p.mail_config)
    mail = Mail(current_app)
    with current_app.app_context():
        msg = Message(email['subject'], sender=email['sender'] or p.mail_config['MAIL_DEFAULT_SENDER'], recipients=email['recipients'])
        msg.body = email['text_body']
        msg.html = email['html_body']
        mail.send(msg)
