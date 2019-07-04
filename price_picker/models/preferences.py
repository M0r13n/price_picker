from price_picker import db
from flask import current_app


class Preferences(db.Model):
    """ Store User Preferences here"""
    __tablename__ = 'preferences'
    id = db.Column(db.Integer, primary_key=True)
    imei_required = db.Column(db.Boolean, default=False)
    first_name_required = db.Column(db.Boolean, default=False)
    last_name_required = db.Column(db.Boolean, default=False)
    phone_required = db.Column(db.Boolean, default=False)
    mail_required = db.Column(db.Boolean, default=True)

    # Mail Settings

    @property
    def mail_password(self):
        raise AttributeError('password is not a readable attribute')

    @classmethod
    def load_settings(cls):
        """
        Load config into memory
        """
        p = cls.query.first()
        if p is None:
            return
        current_app.config['IMEI_REQUIRED'] = p.imei_required
        current_app.config['FIRST_NAME_REQUIRED'] = p.first_name_required
        current_app.config['LAST_NAME_REQUIRED'] = p.last_name_required
        current_app.config['PHONE_REQUIRED'] = p.phone_required
        current_app.config['MAIL_REQUIRED'] = p.mail_required
