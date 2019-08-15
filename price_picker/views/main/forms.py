from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email
from flask import current_app
from price_picker.models import Shop


class LoginForm(FlaskForm):
    username = StringField(
        "Nutzername",
        validators=[
            DataRequired(),
        ],
    )
    password = PasswordField(
        "Passwort",
        validators=[
            DataRequired()
        ],
    )
    remember_me = BooleanField('Angemeldet bleiben', default=True)


class SelectRepairForm(FlaskForm):
    repairs = SelectMultipleField(
        coerce=int,
        choices=[]
    )
    color = StringField()


class ContactForm(FlaskForm):
    first_name = StringField(
        "Vorname",
        validators=[
            Length(max=60, message='Max 60 Zeichen')
        ],
    )
    last_name = StringField(
        "Nachname",
        validators=[
            Length(max=60, message='Max 60 Zeichen'),
        ],
    )
    phone = StringField(
        "Telefon",
        validators=[
            Length(max=25, message="Die Telefonnummer ist nicht gültig.")
        ],
        description="Die Telefonnummer ist optional."
    )
    imei = StringField(
        "IMEI",
        validators=[
            Length(max=40, message="Die IMEI kann maximal 40 Zeichen enthalten.")
        ],
        description="Die IMEI ist eine 15 stellige Numemr und dient der eindeutigen Identifizierung Ihres Geräts. "
                    "Diese können Sie in der Regel durch die Eingabe von *#06# in Ihrer Telefonapp herausfinden. "
    )
    email = StringField(
        "Email Adresse",
        validators=[
            Email(message='Gib eine gültige Mail Adresse an'),
            Length(max=120, message="Max 120 Zeichen")
        ],
        description="Bitte achten Sie auf die Korrektheit der Email. Wir können uns sonst ggf. nicht bei Ihnen melden."
    )
    confirm = SubmitField(
        "Zahlungspflichtig bestellen"
    )
    shop = QuerySelectField(
        "Shop",
        query_factory=Shop.query_factory_all,
        validators=[
            DataRequired(message="Bitte wähle einen Shop")
        ],
        description="In welchem Shop soll die Reparatur durchgeführt werden?"
    )


class AddressContactForm(ContactForm):
    customer_street = StringField(
        "Straße, Hausnummer",
        validators=[
            Length(max=128, message="Max 128 Zeichen.")
        ]
    )
    customer_postal_code = StringField(
        "Postleitzahl",
        validators=[
            Length(max=32, message="Max 32 Zeichen.")
        ]
    )
    customer_city = StringField(
        "Stadt",
        validators=[
            Length(max=128, message="Max 128 Zeichen.")
        ]
    )


def contact_form_factory(preferences, order=True):
    form = AddressContactForm() if current_app.config.get('ADDRESS_REQUIRED') else ContactForm()
    if 'FIRST_NAME_REQUIRED' in preferences.keys() and preferences['FIRST_NAME_REQUIRED']:
        setattr(form.first_name, 'validators', [*form.first_name.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'LAST_NAME_REQUIRED' in preferences.keys() and preferences['LAST_NAME_REQUIRED']:
        setattr(form.last_name, 'validators', [*form.last_name.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'MAIL_REQUIRED' in preferences.keys() and preferences['MAIL_REQUIRED']:
        setattr(form.email, 'validators', [*form.email.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'PHONE_REQUIRED' in preferences.keys() and preferences['PHONE_REQUIRED']:
        setattr(form.phone, 'validators', [*form.phone.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'IMEI_REQUIRED' in preferences.keys() and preferences['IMEI_REQUIRED']:
        setattr(form.imei, 'validators', [*form.imei.validators, DataRequired("Dieses Feld wird benötigt")])
    if not order:
        form.confirm.label.text = "Kostenvoranschlag anfordern"
    return form
