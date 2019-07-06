from wtforms.validators import ValidationError
from price_picker.models import Device, Manufacturer, Color
from flask_login import current_user


class UniqueDeviceName(object):
    def __init__(self, message=None):
        if message is None:
            message = 'Dieses Gerät existiert bereits.'
        self.message = message

    def __call__(self, form, field):
        device = Device.query.filter_by(name=field.data).first()
        if device is not None:
            raise ValidationError(self.message)


class UniqueManufacturerName(object):
    def __init__(self, message=None):
        if message is None:
            message = 'Dieser Hersteller existiert bereits.'
        self.message = message

    def __call__(self, form, field):
        manufacturer = Manufacturer.query.filter_by(name=field.data).first()
        if manufacturer is not None:
            raise ValidationError(self.message)


class UniqueColorName(object):
    def __init__(self, message=None):
        if message is None:
            message = 'Diese Farbe existiert bereits.'
        self.message = message

    def __call__(self, form, field):
        c = Color.query.filter_by(name=field.data).first()
        if c is not None:
            raise ValidationError(self.message)


class MatchesOldPassword(object):
    def __init__(self, message=None):
        if message is None:
            message = 'Das Passwort ist nicht korrekt.'
        self.message = message

    def __call__(self, form, field):
        if not current_user.verify_password(field.data):
            raise ValidationError(self.message)
