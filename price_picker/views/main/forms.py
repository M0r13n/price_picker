from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired


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
