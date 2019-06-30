from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, Email


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


class ContactForm(FlaskForm):
    first_name = StringField(
        "Vorname",
        validators=[
            DataRequired(message="Es wird ein Vorname benötigt"),
            Length(min=2, max=60, message='Der Name muss zwischen 2 und 60 Zeichen haben!')
        ],
    )
    last_name = StringField(
        "Nachname",
        validators=[
            DataRequired(message="Es wird ein Nachname benötigt"),
            Length(min=2, max=60, message='Der Name muss zwischen 2 und 60 Zeichen haben!'),
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

    color = StringField(
        "Farbe",
        validators=[
            DataRequired(message="Es wird ein Nachname benötigt"),
            Length(min=3, max=30, message="Die Farbe sollte zwischen 3 und 30 Zeichen enthalten")
        ],
        description="Die Farbe ist zwingend erforderlich, damit wir das richtige Ersatzteil für Sie bestellen können."
    )

    email = StringField(
        "Email Adresse",
        validators=[
            DataRequired(message="Es wird eine Mail benötigt"),
            Email(message='Gib eine gültige Mail Adresse an'),
            Length(min=6, max=40, message='Die Mail sollte zwischen 6 und 40 Zeichen haben!'),
        ],
        description="Bitte achten Sie auf die Korrektheit der Email. Wir können uns sonst ggf. nicht bei Ihnen melden."
    )
    confirm = SubmitField(
        "Bestellung abschließen"
    )
