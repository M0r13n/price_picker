from price_picker import db
from price_picker.common.database import CRUDMixin
from flask import current_app, has_app_context
from sqlalchemy import event
import rncryptor


class Encryption:
    NONE = 0
    TLS = 1
    SSL = 2


class Preferences(db.Model, CRUDMixin):
    """ Store User Preferences here"""
    __tablename__ = 'preferences'
    id = db.Column(db.Integer, primary_key=True)
    imei_required = db.Column(db.Boolean, default=False)
    first_name_required = db.Column(db.Boolean, default=False)
    last_name_required = db.Column(db.Boolean, default=False)
    phone_required = db.Column(db.Boolean, default=False)
    mail_required = db.Column(db.Boolean, default=True)
    address_required = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(128))
    mail = db.Column(db.String(128))
    active_sale = db.Column(db.Boolean, default=False)
    sale_amount = db.Column(db.Integer, default=0)

    # Mail Settings
    mail_port = db.Column(db.Integer, default=587)
    mail_server = db.Column(db.String(128))
    mail_encryption = db.Column(db.Integer, default=1)
    mail_username = db.Column(db.String(128))
    mail_default_sender = db.Column(db.String(128))
    mail_password_encrypted = db.Column(db.LargeBinary)
    order_copy_mail_address = db.Column(db.String(128))

    @property
    def mail_password(self):
        raise AttributeError('password is not a readable attribute')

    def encrypt_mail_password(self, password):
        """
        Accepts the clear text password and stores it encrypted with the app´s secret key.

        :param password: clear text password
        :return:
        """
        if not has_app_context:
            raise ValueError("No App Context")
        secret_key = current_app.config['SECRET_KEY']
        cryptor = rncryptor.RNCryptor()
        encrypted_password = cryptor.encrypt(password, secret_key)
        self.mail_password_encrypted = encrypted_password
        db.session.commit()
        current_app.logger.info("Successfully encrypted mail password.")

    def decrypt_mail_password(self):
        """
        Decrypts the encrypted password with the app´s secret key.
        :return: decrypted password
        """
        if not has_app_context:
            raise ValueError("No App Context")
        secret_key = current_app.config['SECRET_KEY']
        cryptor = rncryptor.RNCryptor()
        decrypted_password = cryptor.decrypt(self.mail_password_encrypted, secret_key)
        current_app.logger.info("Successfully decrypted mail password.")
        return decrypted_password

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
        current_app.config['ADDRESS_REQUIRED'] = p.address_required
        current_app.config['USER_MAIL'] = p.mail
        current_app.config['USER_PHONE'] = p.phone_number
        current_app.config['ACTIVE_SALE'] = p.active_sale
        current_app.config['SALE_AMOUNT'] = p.sale_amount

    @property
    def mail_config(self):
        """
        Load mail config settings
        """
        config = {
            'MAIL_USERNAME': self.mail_username,
            'MAIL_PASSWORD': self.decrypt_mail_password(),
            'MAIL_SERVER': self.mail_server,
            'MAIL_USE_TLS': self.mail_encryption == Encryption.TLS,
            'MAIL_USE_SSL': self.mail_encryption == Encryption.SSL,
            'MAIL_DEFAULT_SENDER': self.mail_default_sender or self.mail_username,
            'MAIL_PORT': self.mail_port
        }
        return config


@event.listens_for(Preferences, 'after_update')
def receive_after_update(mapper, connection, target):
    Preferences.load_settings()
