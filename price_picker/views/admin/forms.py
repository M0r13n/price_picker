from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, PasswordField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, Email, Optional, EqualTo
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from price_picker.models import Manufacturer, Picture, Color, Encryption
from .validators import UniqueDeviceName, UniqueManufacturerName, UniqueColorName, MatchesOldPassword
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
    address_required = BooleanField(
        "Anschrift erforderlich",
        default=False
    )
    phone_number = StringField(
        "Service Telefonnummer",
        validators=[Length(max=128, message="128 Zeichen maximal.")],
        description="Diese Telefonnummer wird dem Kunden in Hilfetexten angezeigt."
    )
    mail = StringField(
        "Service Email",
        validators=[Length(max=128, message="128 Zeichen maximal."), Email(message="Eine gültige Email ist erforderlich.")],
        description="Diese Email wird dem Kunden in Hilfetexten angezeigt."
    )
    privacy_statement = StringField(
        "Link zur persönlichen Datenschutzerklärung.",
        validators=[Length(max=256, message="256 Zeichen maximal.")],
        description="Dieser Link wird dem Kunden bei Abgabe seiner Daten präsentiert. Ein falscher oder fehlender Link kann Grund"
                    "für eine Abmahnung sein."
    )


class MailSettingsForm(FlaskForm):
    mail_encryption = SelectField(
        "Transportverschlüsselung",
        choices=[(Encryption.NONE, 'Keine'), (Encryption.TLS, 'TLS'), (Encryption.SSL, 'SSL')],
        coerce=int,
        default=False,
        description="Wenn aktiviert werden die Mails TLS-verschlüsselt übertragen. Beachten Sie die Vorgaben ihres Providers."
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
    order_copy_mail_address = StringField(
        "Bestellkopie senden",
        validators=[Optional(), Email(message="Keine gültige Mail")],
        description="An die hier angegebene Mail wird eine Kopie der Kundenanfragen gesendet."
    )


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        "Altes Passwort",
        validators=[
            DataRequired(message="Altes Passwort erforderlich."),
            MatchesOldPassword()
        ]
    )
    password = PasswordField(
        "Neues Passwort",
        validators=[
            DataRequired(message="Neues Passwort erforderlich."),
            Length(min=6, message="Mehr als 6 Zeichen erforderlich.")]
    )
    confirm = PasswordField(
        "Passwort bestätigen",
        validators=[
            DataRequired(message="Neues Passwort erforderlich."),
            EqualTo("password", message="Passwörter stimmen nicht überein."),
        ],
    )


class CsvUploadForm(FlaskForm):
    csv = FileField(
        "CSV Upload",
        validators=[
            FileRequired(message="Keine Datei angegeben."),
            FileAllowed(['csv'], 'Nur .csv Datein werden unterstützt.')
        ]
    )


class SaleForm(FlaskForm):
    active_sale = BooleanField(
        "Aktiver Sale",
        description="Soll eine Rabatt Aktion laufen?"
    )
    sale_amount = IntegerField(
        "Rabattwert",
        validators=[NumberRange(max=50, message="Der Sale kann maximal 50€ betragen")],
        description="Dieser Rabattwert wird auf alle Reparaturen angerechnet, die über den PricePicker abgeschlossen werden"

    )


class EmailTestForm(FlaskForm):
    recipient = StringField(
        "Empfänger",
        validators=[
            Email(message="Keine gültige Mail"),
            Length(max=128, message="Maximal 128 Zeichen")
        ],
        description="Sende eine Mail an diese Zieladresse"

    )
