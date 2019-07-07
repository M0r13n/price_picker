from price_picker import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from price_picker.common.database import CRUDMixin


class User(UserMixin, CRUDMixin, db.Model):
    """Basic user model
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return "<User %s>" % self.username

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
