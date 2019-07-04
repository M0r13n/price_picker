from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from price_picker.models import Manufacturer, Picture, Color
from .validators import UniqueDeviceName, UniqueManufacturerName, UniqueColorName
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
        validators=[
            DataRequired(
                message="Erforderlich"
            )
        ]
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
        description="Mehrfachauswahl möglich.",
        validators=[
            DataRequired(
                message="Es muss mindestens eine Farbe gewählt werden."
            )
        ]

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
            Length(min=1, max=64, message="Der Name muss zwischen 1 und 64 Zeichen lang sein")
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
            Length(min=1, max=64, message="Der Name muss zwischen 1 und 64 Zeichen lang sein")
        ],
    )

    price = IntegerField(
        "Preis",
        validators=[
            DataRequired(message="Gib einen Preis an")
        ],
    )


class NewColorForm(FlaskForm):
    name = StringField(
        "Farbe",
        validators=[
            DataRequired(message="Wie heißt die Farbe?"),
            Length(min=1, max=128, message="Der Name muss zwischen 1 und 128 Zeichen lang sein"),
            UniqueColorName()
        ],
    )

    color_code = StringField(
        "HTML Farb Code",
        validators=[
            DataRequired(message="Die Farbe braucht einen gültigen Code im HEX-Format"),
            Length(min=7, max=7, message="Der Code muss genau 7 Zeichen inklusive # enthalten"),
            Regexp('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', message="Der Code muss ein gültiges Format haben")
        ],
        description="Der Farb Code dient der Darstellung in der Nutzeransicht und muss im HEX-Format angegeben werden"
    )


class ContactSettingsForm(FlaskForm):
    """
    Define which data should be necessary
    """
    imei_required = BooleanField(
        "IMEI erforderlich",
        default=False
    )
    first_name_required = BooleanField(
        "Vorname erforderlich",
        default=False
    )
    last_name_required = BooleanField(
        "Nachname erforderlich",
        default=False
    )
    mail_required = BooleanField(
        "Mail erforderlich",
        default=True
    )
    phone_required = BooleanField(
        "Telefonnummer erforderlich",
        default=False
    )


class MailSettingsForm(FlaskForm):
    mail_server_activated = BooleanField(
        "Mail Server aktiviert",
        default=False
    )
    mail_server = StringField(
        "Mail Server",
        validators=[Length(max=128, message="Maximal 128 Zeichen")],
        description="Der Server für ausgehende Mails, z.B. smtp.googlemail.com"
    )
    mail_port = IntegerField(
        "Mail Port",
        validators=[NumberRange(max=55555, message="Maximal 55555")],
        description="Der Port für den Mail Server, z.B. 587"
    )
    mail_username = StringField(
        "Nutzername",
        validators=[Length(max=128, message="Maximal 128 Zeichen")],
        description="Der Nutzername für den Mail Account. In der Regel die Mail-Adresse"
    )
    mail_password = PasswordField(
        "Mail Passwort",
        validators=[Length(max=128, message="Maximal 128 Zeichen")],
        description="Das Passwort wird verschlüsselt in der Datenbank gespeichert."
    )
    mail_default_sender = StringField(
        "Mail Absender",
        validators=[Length(max=128, message="Maximal 128 Zeichen")],
        description="Die Absende Adresse. Diese entspricht in der Regel der Mail Adresse."
    )
