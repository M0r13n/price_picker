from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from price_picker.models import Manufacturer, Picture, Color
from .validators import UniqueDeviceName, UniqueManufacturerName
from price_picker.common.fields import MultiCheckboxField


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

    picture = QuerySelectField(
        label="Bild",
        query_factory=Picture.query_factory_all,
        get_pk=lambda i: i.name,
        get_label=lambda i: i.name,
        allow_blank=True, blank_text='Bild wählen'

    )

    colors = MultiCheckboxField(
        label="Farbe",
        query_factory=Color.query_factory_all,
        get_pk=lambda i: i.name,
        get_label=lambda i: i.name,
        description="Mehrfachauswahl möglich."

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

    picture = QuerySelectField(
        label="Bild",
        query_factory=Picture.query_factory_all,
        get_pk=lambda i: i.name,
        get_label=lambda i: i.name,
        allow_blank=True, blank_text='Bild wählen'

    )


class EditManufacturerForm(NewManufacturerForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(message="Gib einen Namen an"),
            Length(min=1, max=64, message='Der Name muss zwischen 1 und 64 Zeichen lang sein')
        ],
    )

    picture = QuerySelectField(
        label="Bild",
        query_factory=Picture.query_factory_all,
        get_pk=lambda i: i.name,
        get_label=lambda i: i.name,
        allow_blank=True, blank_text='Bild wählen'

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
