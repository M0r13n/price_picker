from flask import render_template, Blueprint, flash, redirect, url_for, session, request
from price_picker.models import Manufacturer, Device, User, Repair, Preferences
from .forms import LoginForm, SelectRepairForm, ContactForm, SelectColorForm
from price_picker import db
from price_picker.common.decorators import step, sub_title
from flask_login import login_user, logout_user, login_required

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    """
    1st Step.

    Entry Point for choosing a repair.
    The customer selects the desired manufacturer, e.g. Apple.
    Redirects to select_device.
    """
    manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
    return render_template("main/home.html",
                           manufacturers=manufacturers)


@main_blueprint.route("/manufacturer/<int:manufacturer_id>")
@step(1)
@sub_title("Geräteauswahl")
def select_device(manufacturer_id, **kwargs):
    """
    2nd Step.

    The customer selects the desired device, e.g. iPhone X.
    Redirects to select_color.
    """
    devices = Device.query.filter(Device.manufacturer_id == manufacturer_id).all()
    return render_template("main/select_device.html",
                           devices=devices,
                           manufacturer_id=manufacturer_id,
                           **kwargs)


@main_blueprint.route("/device/<int:device_id>/color", methods=['GET', 'POST'])
@step(2)
@sub_title("Farbauswahl")
def choose_color(device_id, **kwargs):
    """
    3rd Step.

    The customer selects the desired color, e.g. black.
    Redirects to select_repair.
    """
    device = Device.query.get_or_404(device_id)
    form = SelectColorForm()
    form.colors.choices = [(c.name, c.name) for c in device.colors]
    if form.validate_on_submit():
        session['color'] = form.colors.data
        return redirect(url_for('main.select_repair', device_id=device_id))
    return render_template('main/choose_color.html',
                           device=device,
                           form=form,
                           **kwargs)


@main_blueprint.route("/device/<int:device_id>", methods=['GET', 'POST'])
@step(3)
@sub_title("Defektauswahl")
def select_repair(device_id, **kwargs):
    """
    4th Step.

    The customer selects the desired repair, e.g. display.
    Redirects to summary or to estimate_of_costs depending on the customer choice.
    """
    device = Device.query.get_or_404(device_id)
    form = SelectRepairForm()
    form.repairs.choices = [(r.id, r.name) for r in device.repairs]
    if form.validate_on_submit():
        session['repair_ids'] = form.repairs.data
        if request.form.get('estimate') is not None:
            return redirect(url_for('.estimate_of_costs', device_id=device_id))
        return redirect(url_for('.summary', device_id=device_id))
    return render_template('main/select_repair.html',
                           device=device,
                           form=form,
                           **kwargs)


@main_blueprint.route("/costs/<int:device_id>", methods=['GET', 'POST'])
@step(5)
@sub_title("Kostenvoranschlag")
def estimate_of_costs(device_id, **kwargs):
    """
    5th Step - Alternative.

    Instead of placing an order, the user can also request an estimate of costs.
    This will be sent via mail to the customer.
    """
    color = session['color'] if 'color' in session.keys() else 'default'
    device = Device.query.get_or_404(device_id)
    repair_ids = session['repair_ids']
    repairs = db.session.query(Repair).filter(Repair.id.in_(repair_ids)).all()
    form = ContactForm()
    form.confirm.label.text = "Kostenvoranschlag anfordern!"
    if form.validate_on_submit():
        flash(f'Wir haben den Kostenvoranschlag an {form.email.data} versandt!', 'success')
        return redirect(url_for('main.thank_you'))
    return render_template('main/complete.html',
                           form=form,
                           device_id=device_id,
                           **kwargs)


@main_blueprint.route("/summary/<int:device_id>")
@step(4)
@sub_title("Auftragsübersicht")
def summary(device_id, **kwargs):
    """
    5th Step - Default.

    The customer confirms the summary which includes a list of selected repairs and an estimated price.
    Redirects to final completion.
    """
    color = session['color'] if 'color' in session.keys() else 'default'
    device = Device.query.get_or_404(device_id)
    repair_ids = session['repair_ids']
    repairs = db.session.query(Repair).filter(Repair.id.in_(repair_ids)).all()
    return render_template('main/summary.html',
                           repairs=repairs,
                           device=device,
                           total=sum([r.price for r in repairs]),
                           color=color,
                           **kwargs)


@main_blueprint.route("/complete/<int:device_id>", methods=['GET', 'POST'])
@step(5)
@sub_title("Abschluss")
def complete(device_id, **kwargs):
    """
    6th Step.

    The customer enters it´s personal data.
    After that the order is processed and both (the customer and the shop-owner) will receive an confirmation mail.
    Redirect to the 1st page and closes the circle.
    """
    form = ContactForm()
    if form.validate_on_submit():
        if 'repair_ids' not in session.keys() or not isinstance(session['repair_ids'], list):
            flash('Da ist etwas schief gelaufen. Es tut uns Leid. Wähle deine Reparatur erneut.', 'danger')
            return redirect(url_for('main.select_repair', device_id=device_id))
        repairs = db.session.query(Repair).filter(Repair.id.in_(session['repair_ids'])).all()
        print(repairs)
        flash('Wir haben ihre Anfrage erhalten!', 'success')
        return redirect(url_for('main.thank_you'))
    return render_template('main/complete.html',
                           form=form,
                           device_id=device_id,
                           **kwargs)


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


@main_blueprint.before_app_first_request
def load_preferences():
    """ Load preferences on first start-up"""
    Preferences.load_settings()
