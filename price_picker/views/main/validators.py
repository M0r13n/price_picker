from wtforms.validators import ValidationError
from price_picker.models import CouponCode


class CouponCodeValidator(object):
    def __init__(self, message=None):
        if message is None:
            message = 'Ungültiger Code.'
        self.message = message

    def __call__(self, form, field):
        code = CouponCode.query.filter_by(code=field.data).first()
        if not code:
            raise ValidationError(self.message)
