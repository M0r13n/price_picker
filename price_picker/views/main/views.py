from flask import render_template, Blueprint, flash, redirect, url_for
from price_picker.common.next_page import next_page
from price_picker.models import Manufacturer, Device
from .forms import LoginForm
from price_picker.models import User
from flask_login import login_user, logout_user, login_required

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
    return render_template("main/home.html",
                           manufacturers=manufacturers)


@main_blueprint.route("/manufacturer/<int:manufacturer_id>")
def select_device(manufacturer_id):
    devices = Device.query.filter(Device.manufacturer_id == manufacturer_id).all()
    return render_template("main/select_device.html", devices=devices, manufacturer_id=manufacturer_id)


@main_blueprint.route("/device/<int:device_id>")
def select_repair(device_id):
    device = Device.query.get_or_404(device_id)
    return render_template('main/select_repair.html', device=device)


@main_blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('Du wurdest erfolgreich eingeloggt', 'success')
            return redirect(url_for('.home'))
        flash('Falsches Passwort oder Nutzername', 'danger')
    return render_template('main/login.html', form=form)


@main_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du wurdest abgemeldet. Byyee!', 'success')
    return redirect(url_for('.home'))
