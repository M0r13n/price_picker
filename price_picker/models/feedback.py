from price_picker import db
import datetime as dt
from price_picker.common.database import CRUDMixin


class Feedback(db.Model, CRUDMixin):
    __tablename__ = 'customer_feedback'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.now)
    customer_name = db.Column(db.String(128), nullable=True)
    customer_email = db.Column(db.String(128), nullable=True)
    subject = db.Column(db.Text)
    details = db.Column(db.Text)

    def __repr__(self):
        return f"<Feeback from {self.created_at}>"
