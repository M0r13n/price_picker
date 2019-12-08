import re
import random

from flask import (
    render_template,
    Blueprint,
    flash,
    redirect,
    url_for,
    session,
    request,
    current_app,
    send_from_directory,
    jsonify
)
from flask_login import (
    login_user,
    logout_user,
    login_required
)

from .forms import (
    LoginForm,
    SelectRepairForm,
    contact_form_factory,
    ContactForm,
    AddressContactForm
)
from price_picker import db
from price_picker.models import (
    Manufacturer,
    Device,
    User,
    Repair,
    Preferences,
    Enquiry,
    Mail,
    CouponCode
)
from price_picker.tasks.mail import (
    CustomerConfirmationEmail,
    send_email_task,
    EnquiryReceivedEmail,
    configured_confirmation_recipient
)

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    """
    1st Step.

    Entry Point for choosing a repair.
    The customer selects the desired manufacturer, e.g. Apple.
    """
    manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
    return render_template("main/home.html",
                           manufacturers=manufacturers)


@main_blueprint.route("/manufacturer/<int:manufacturer_id>")
def select_device(manufacturer_id):
    """
    2nd Step.

    The customer selects the desired device, e.g. iPhone X.
    """
    devices = Device.query.filter(Device.manufacturer_id == manufacturer_id).order_by(Device.name).all()
    return render_template("main/select_device.html",
                           devices=devices,
                           manufacturer_id=manufacturer_id)


@main_blueprint.route("/device/<int:device_id>/color", methods=['GET', 'POST'])
def choose_color(device_id):
    """
    3rd Step.

    The customer selects the desired color, e.g. black.
    """
    device = Device.query.get_or_404(device_id)
    return render_template('main/choose_color.html',
                           device=device)


@main_blueprint.route("/device/<int:device_id>", methods=['GET', 'POST'])
def select_repair(device_id):
    """
    4th Step.

    The customer selects the desired repair, e.g. display.
    """
    device = Device.query.get_or_404(device_id)
    repairs = device.repairs.order_by(Repair.name)
    form = SelectRepairForm()
    form.repairs.choices = [(r.id, r.name) for r in repairs]
    if form.validate_on_submit():
        session['repair_ids'] = form.repairs.data
        session['color'] = form.color.data or 'default'
        if request.form.get('estimation') is not None:
            return redirect(url_for('.complete', device_id=device_id))
        return redirect(url_for('.summary', device_id=device_id))
    return render_template('main/select_repair.html',
                           device=device,
                           form=form,
                           repairs=repairs)


@main_blueprint.route("/summary/<int:device_id>")
def summary(device_id):
    """
    5th Step - Default.

    The customer confirms the summary which includes a list of selected repairs and an estimated price.
    """
    color = session['color'] if 'color' in session.keys() else 'default'
    device = Device.query.get_or_404(device_id)
    if not 'repair_ids' in session.keys():
        flash('Es wurde keine Reparatur ausgwählt.', 'danger')
        current_app.logger.warning('Missing key \"repair_ids\" in current session.')
        return redirect(url_for('main.select_repair', device_id=device.id))
    repair_ids = session['repair_ids']
    repairs = db.session.query(Repair).filter(Repair.id.in_(repair_ids)).all()
    return render_template('main/summary.html',
                           repairs=repairs,
                           device=device,
                           total=max(sum([r.price for r in repairs]) - int(current_app.config['ACTIVE_SALE']) *
                                     current_app.config[
                                         'SALE_AMOUNT'], 0),
                           color=color)


@main_blueprint.route("/complete/<int:device_id>", methods=['GET', 'POST'])
def complete(device_id):
    """
    6th Step.

    The customer enters it´s personal data.
    After that the order is processed and both (the customer and the shop-owner) will receive an confirmation mail.
    """
    order = request.args.get('order', False, bool)
    device = Device.query.get_or_404(device_id)
    form = contact_form_factory(current_app.config, order)
    if form.validate_on_submit():
        if not _complete(order, device, form):
            flash('Es wurde keine Reparatur ausgwählt.', 'danger')
            return redirect(url_for('main.select_repair', device_id=device.id))

        flash('Wir haben Ihre Anfrage erhalten!', 'success')
        return redirect(url_for('main.thank_you'))
    return render_template('main/complete.html',
                           form=form,
                           device_id=device_id)


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
    flash('Abmeldung erfolgreich!', 'success')
    return redirect(url_for('.home'))


@main_blueprint.before_app_first_request
def load_preferences():
    """ Load preferences on first start-up"""
    Preferences.load_settings()
    current_app.logger.info('Successfully loaded user preferences')


@main_blueprint.route('/robots.txt')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])


# API
@main_blueprint.route('/wof/submit', methods=["POST"])
def wheel_of_fortune_submit():
    """
    Handle a submission of a wheel-of-fortune form.
    A code is only generated if a seemingly valid email is provided.
    Also the server decides if the user wins to prevent cheating.
    """
    mail_check = re.compile('[^@]+@[^@]+\.[^@]+')
    submitted_email = request.form.get('email', default=None)
    code = ''

    # check if the mail matches a normal mail pattern: xx@yy.zz
    if not submitted_email or not mail_check.match(submitted_email):
        return jsonify(dict(status='invalid-mail')), 400

    # prevent multiple use of the same mail
    if Mail.query.filter_by(mail=submitted_email.lower()).first():
        return jsonify(dict(status='invalid-mail')), 400

    # store mail
    Mail.create(mail=submitted_email.lower())

    # randomly choose a discount (or no discount)
    value = random.choice(CouponCode.VALUES + [0])
    # generate a coupon code
    if value:
        code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i in range(0, 6):
            slice_start = random.randint(0, len(code_chars) - 1)
            code += code_chars[slice_start: slice_start + 1]

        # store the coupon code in db
        CouponCode.create(code=code, value=value)

    # finally return both the discount-value and the coupon code
    return jsonify(dict(status='ok', code=code, value=value)), 201


@main_blueprint.route('/code/verify', methods=["POST"])
def verify_code():
    """
    Verify if a code is valid, aka if we have such code stored in database.
    """
    if not request.json or 'code' not in request.json:
        return jsonify(dict(status='bad-request', message="Missing attribute \"code\" in request-json.")), 400

    code = request.json.get('code')
    code = CouponCode.query.filter_by(code=code).first()
    if not code:
        return jsonify(dict(status='invalid-code')), 404

    return jsonify(dict(status='ok', code=code.code, value=code.value)), 200


# NO VIEW FUNCTIONS


def _send_mails(form, enquiry):
    # send mails as a background task via celery
    if form.email.data:
        send_email_task.delay(CustomerConfirmationEmail(recipients=form.email.data).__dict__)
    rp = configured_confirmation_recipient()
    if rp:
        send_email_task.delay(EnquiryReceivedEmail(recipients=rp, enquiry=enquiry).__dict__)


def _complete(order: bool, device: Device, form: ContactForm) -> bool:
    if 'repair_ids' not in session.keys() or not isinstance(session['repair_ids'], list):
        current_app.logger.error('Missing key \"repair_ids\" in current session.')
        return False

    repairs = db.session.query(Repair).filter(Repair.id.in_(session['repair_ids'])).all()
    color = session['color'] if 'color' in session.keys() else 'default'

    discount = 0
    if form.coupon.data:
        code = CouponCode.query.filter_by(code=form.coupon.data).first()
        if code:
            discount = code.value
            # delete the code to free up space and prevent reuse
            code.delete()

    # check which form was submitted
    if isinstance(form, AddressContactForm):
        e = Enquiry.create(color=color,
                           device=device,
                           repairs=repairs,
                           customer_email=form.email.data,
                           customer_first_name=form.first_name.data,
                           customer_last_name=form.last_name.data,
                           customer_phone=form.phone.data,
                           customer_street=form.customer_street.data,
                           customer_city=form.customer_city.data,
                           customer_postal_code=form.customer_postal_code.data,
                           sale=current_app.config['SALE_AMOUNT'] if current_app.config['ACTIVE_SALE'] else discount,
                           imei=form.imei.data,
                           shop=form.shop.data.name,
                           name="Reparaturauftrag" if order else "Kostenvoranschlag")
    else:
        e = Enquiry.create(color=color,
                           device=device,
                           repairs=repairs,
                           customer_email=form.email.data,
                           customer_first_name=form.first_name.data,
                           customer_last_name=form.last_name.data,
                           customer_phone=form.phone.data,
                           sale=current_app.config['SALE_AMOUNT'] if current_app.config['ACTIVE_SALE'] else discount,
                           imei=form.imei.data,
                           shop=form.shop.data.name,
                           name="Reparaturauftrag" if order else "Kostenvoranschlag")
    _send_mails(form, e)
    return True
