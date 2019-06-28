from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from price_picker.models import Manufacturer
from .validators import UniqueDeviceName, UniqueManufacturerName


class NewDeviceForm(FlaskForm):
    name = StringField(
        "Gerätename",
        validators=[
            DataRequired(message="Gib einen Namen an"),
            Length(min=1, max=64, message='Der Name muss zwischen 1 und 64 Zeichen lang sein'),
            UniqueDeviceName()
        ],
    )

    manufacturer = QuerySelectField(
        label='Hersteller',
        query_factory=Manufacturer.query_factory_all,
        get_pk=lambda i: i.id,
        get_label=lambda i: i.name,
        allow_blank=True, blank_text='Hersteller wählen',
        validators=[DataRequired(message="Erforderlich")]
    )


class EditDeviceForm(NewDeviceForm):
    name = StringField(
        "Gerätename",
        validators=[
            DataRequired(message="Gib einen Namen an"),
            Length(min=1, max=64, message='Der Name muss zwischen 1 und 64 Zeichen lang sein')
        ],
    )


class NewManufacturerForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(message="Gib einen Namen an"),
            Length(min=1, max=64, message='Der Name muss zwischen 1 und 64 Zeichen lang sein'),
            UniqueManufacturerName()
        ],
    )


class EditManufacturerForm(NewManufacturerForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(message="Gib einen Namen an"),
            Length(min=1, max=64, message='Der Name muss zwischen 1 und 64 Zeichen lang sein')
        ],
    )


class DeleteForm(FlaskForm):
    """ Only for CSRF Protection"""
    submit = SubmitField('Löschen')


class NewRepairForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(message="Gib einen Namen an"),
            Length(min=1, max=64, message='Der Name muss zwischen 1 und 64 Zeichen lang sein')
        ],
    )

    price = IntegerField(
        "Preis",
        validators=[
            DataRequired(message="Gib einen Preis an")
        ],
    )
