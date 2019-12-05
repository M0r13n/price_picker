from price_picker import db
from price_picker.common.database import CRUDMixin


class CouponCode(CRUDMixin, db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        return "<Coupon %s>" % self.mail
