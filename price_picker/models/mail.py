from price_picker import db
from price_picker.common.database import CRUDMixin


class Mail(CRUDMixin, db.Model):
    __tablename__ = 'mails'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(200), unique=True, nullable=False)

    def __repr__(self):
        return "<Mail %s>" % self.mail
