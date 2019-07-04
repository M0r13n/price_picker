from price_picker import db
from flask import current_app, has_app_context
import rncryptor
import time


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
    mail_server_activated = db.Column(db.Boolean, default=True)
    mail_server = db.Column(db.String(128))
    mail_port = db.Column(db.Integer, default=587)
    mail_username = db.Column(db.String(128))
    mail_password_encrypted = db.Column(db.LargeBinary)
    mail_default_sender = db.Column(db.String)

    @property
    def mail_password(self):
        raise AttributeError('password is not a readable attribute')

    def encrypt_mail_password(self, password):
        """
        Accepts the clear text password and stores it encrypted with the app´s secret key.

        :param password: clear text password
        :return:
        """
        if not has_app_context():
            raise ValueError("Encryption working outside app context")
        start = time.clock()
        secret_key = current_app.config['SECRET_KEY']
        cryptor = rncryptor.RNCryptor()
        encrypted_password = cryptor.encrypt(password, secret_key)
        self.mail_password_encrypted = encrypted_password
        db.session.commit()
        end = time.clock()
        current_app.logger.info(f'Password encryption took: {end - start} seconds')

    def decrypt_mail_password(self):
        """
        Decrypts the encrypted password with the app´s secret key.
        :return: decrypted password
        """
        if not has_app_context():
            raise ValueError("Decryption working outside app context")
        start = time.clock()
        secret_key = current_app.config['SECRET_KEY']
        cryptor = rncryptor.RNCryptor()
        decrypted_password = cryptor.decrypt(self.mail_password_encrypted, secret_key)
        end = time.clock()
        current_app.logger.info(f'Password decryption took: {end - start} seconds')
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
        current_app.config['MAIL_SERVER_ACTIVATED'] = p.mail_server_activated
        current_app.config['MAIL_SERVER'] = p.mail_server
        current_app.config['MAIL_PORT'] = p.mail_port
        current_app.config['MAIL_USERNAME'] = p.mail_username
        current_app.config['MAIL_PASSWORD'] = p.decrypt_mail_password()
        current_app.config['MAIL_DEFAULT_SENDER'] = p.mail_default_sender or p.mail_username
