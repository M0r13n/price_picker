from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email
from flask import current_app

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


class SelectColorForm(FlaskForm):
    colors = SelectField(
        coerce=str,
        choices=[]
    )


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
        description="Die IMEI dient der eindeutigen Identifizierung Ihres Geräts und ist bei Versicherungsschäden zwingend erforderlich."
    )
    email = StringField(
        "Email Adresse",
        validators=[
            Email(message='Gib eine gültige Mail Adresse an'),
        ],
        description="Bitte achten Sie auf die Korrektheit der Email. Wir können uns sonst ggf. nicht bei Ihnen melden."
    )
    confirm = SubmitField(
        "Zahlungspflichtig bestellen"
    )


class AddressContactForm(ContactForm):
    customer_street = StringField(
        "Straße, Hausnummer",
        validators=[
            Length(max=128, message="Maximal 128 Zeichen.")
        ]
    )
    customer_postal_code = StringField(
        "Postleitzahl",
        validators=[
            Length(max=32, message="Maximal 32 Zeichen.")
        ]
    )
    customer_city = StringField(
        "Stadt",
        validators=[
            Length(max=128, message="Maximal 128 Zeichen.")
        ]
    )


def contact_form_factory(preferences):
    form = AddressContactForm() if current_app.config.get('ADDRESS_REQUIRED') else ContactForm()
    if 'FIRST_NAME_REQUIRED' in preferences.keys() and preferences['FIRST_NAME_REQUIRED']:
        setattr(form.first_name, 'validators', [*form.imei.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'LAST_NAME_REQUIRED' in preferences.keys() and preferences['LAST_NAME_REQUIRED']:
        setattr(form.last_name, 'validators', [*form.imei.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'MAIL_REQUIRED' in preferences.keys() and preferences['MAIL_REQUIRED']:
        setattr(form.email, 'validators', [*form.imei.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'PHONE_REQUIRED' in preferences.keys() and preferences['PHONE_REQUIRED']:
        setattr(form.phone, 'validators', [*form.imei.validators, DataRequired("Dieses Feld wird benötigt")])
    if 'IMEI_REQUIRED' in preferences.keys() and preferences['IMEI_REQUIRED']:
        setattr(form.imei, 'validators', [*form.imei.validators, DataRequired("Dieses Feld wird benötigt")])
    return form
