from flask import render_template, Blueprint, flash, redirect, url_for, session
from price_picker.models import Manufacturer, Device, User, Repair
from .forms import LoginForm, SelectRepairForm, ContactForm
from price_picker import db
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
    form = SelectRepairForm()
    form.repairs.choices = [(r.id, r.name) for r in device.repairs]
    return render_template('main/select_repair.html', device=device, form=form)


@main_blueprint.route("/summary/<int:device_id>", methods=['GET', 'POST'])
def summary(device_id):
    device = Device.query.get_or_404(device_id)
    form = SelectRepairForm()
    form.repairs.choices = [(r.id, r.name) for r in device.repairs]
    if form.validate_on_submit():
        repairs = db.session.query(Repair).filter(Repair.id.in_(form.repairs.data)).all()
        session['repair_ids'] = form.repairs.data
        return render_template('main/summary.html', repairs=repairs, device=device, total=sum([r.price for r in repairs]))
    return render_template('main/summary.html', device=device, total=0)


@main_blueprint.route("/complete/<int:device_id>", methods=['GET', 'POST'])
def complete(device_id):
    form = ContactForm()
    if form.validate_on_submit():
        if 'repair_ids' not in session.keys() or not isinstance(session['repair_ids'], list):
            flash('Da ist etwas schief gelaufen. Es tut uns Leid. Wähle deine Reparatur erneut.', 'danger')
            return redirect(url_for('main.select_repair', device_id=device_id))
        repairs = db.session.query(Repair).filter(Repair.id.in_(session['repair_ids'])).all()
        print(repairs)
        flash('Wir haben ihre Anfrage erhalten!', 'success')
        return redirect(url_for('main.thank_you'))
    return render_template('main/complete.html', form=form, device_id=device_id)


@main_blueprint.route('/thanks')
def thank_you():
    return render_template('main/thank_you.html')


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
