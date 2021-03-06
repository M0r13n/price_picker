from price_picker import db
import datetime as dt
from sqlalchemy.orm import relationship
from price_picker.common.database import CRUDMixin

repairs = db.Table('repairs',
                   db.Column('repair_id', db.Integer, db.ForeignKey('repair.id', ondelete="cascade")),
                   db.Column('enquiry_id', db.Integer, db.ForeignKey('enquiries.id', ondelete="cascade"))
                   )


class Enquiry(db.Model, CRUDMixin):
    __tablename__ = "enquiries"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=dt.datetime.now)
    name = db.Column(db.String(128))
    customer_first_name = db.Column(db.String(128))
    customer_last_name = db.Column(db.String(128))
    customer_email = db.Column(db.String(128))
    customer_phone = db.Column(db.String(128))
    customer_street = db.Column(db.String(128))
    customer_city = db.Column(db.String(128))
    customer_postal_code = db.Column(db.String(32))
    sale = db.Column(db.Integer, default=0)
    imei = db.Column(db.String(64))
    color = db.Column(db.String(64))
    shop = db.Column(db.String(128))
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'))
    device = relationship("Device", back_populates="enquiries")
    repairs = relationship("Repair", secondary=repairs)
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Enquiry ({self.name}) from {self.timestamp.strftime('%d.%m.%Y at %H:%M')}>"

    @property
    def address(self):
        return f"{self.customer_street or '-'}, {self.customer_postal_code or '-'}, {self.customer_street or '-'}"
