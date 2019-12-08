from flask import Blueprint, redirect, url_for, flash, request, render_template, current_app, jsonify
from flask_login import current_user, logout_user
from .forms import NewDeviceForm, EditDeviceForm, NewManufacturerForm, EditManufacturerForm, NewRepairForm, \
    NewColorForm, \
    ContactSettingsForm, MailSettingsForm, ChangePasswordForm, CsvUploadForm, SaleForm, EmailTestForm, AddShopForm
from price_picker.models import Device, Manufacturer, Repair, Color, Preferences, Enquiry, Shop, Mail
from price_picker import db, analytics
from price_picker.common.next_page import next_page
from price_picker.tasks.mail import TestEmail, send_email_task
from price_picker.common.csv_import import RepairCsvImporter
import datetime as dt

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.before_request
def require_login():
    if not current_user.is_authenticated:
        flash('Dieser Bereich erfordert einen Login!', 'danger')
        return redirect(url_for('main.login', next=request.full_path))


# MANUFACTURERS


@admin_blueprint.route('/manufacturer/add', methods=['GET', 'POST'])
def add_manufacturer():
    form = NewManufacturerForm()
    if form.validate_on_submit():
        m = Manufacturer.create(name=form.name.data, picture=form.picture.data)
        flash(f"{m.name} erfolgreich hinzugefügt", "success")
        return redirect(next_page())
    return render_template('admin/manufacturer.html', form=form)


@admin_blueprint.route('/manufacturer/<int:manufacturer_id>/delete', methods=['POST'])
def delete_manufacturer(manufacturer_id):
    m = Manufacturer.query.get_or_404(manufacturer_id).delete()
    flash(f"{m.name} erfolgreich gelöscht", "success")
    return jsonify(status='ok'), 201


@admin_blueprint.route('/manufacturer/<int:manufacturer_id>/edit', methods=['GET', 'POST'])
def edit_manufacturer(manufacturer_id):
    m = Manufacturer.query.get_or_404(manufacturer_id)
    form = EditManufacturerForm(obj=m)
    if form.validate_on_submit():
        if Manufacturer.query.filter(Manufacturer.id != m.id, Manufacturer.name == form.name.data).first() is not None:
            form.name.errors.append("Es gibt bereits ein Hersteller mit diesem Namen")
            return render_template('admin/manufacturer.html', form=form)
        m.name = form.name.data
        m.picture = form.picture.data
        m.save()
        flash(f"{m.name} erfolgreich aktualisiert", "success")
        return redirect(url_for('main.home'))
    return render_template('admin/manufacturer.html', form=form)


# DEVICES


@admin_blueprint.route('/device/add', methods=['GET', 'POST'])
def add_device():
    m = request.args.get('manufacturer_id', None, int)
    form = NewDeviceForm()
    if form.validate_on_submit():
        d = Device().create(name=form.name.data, manufacturer=form.manufacturer.data, picture=form.picture.data,
                            colors=form.colors.data)
        flash("Gerät erfolgreich hinzugefügt", "success")
        return redirect(url_for('main.select_device', manufacturer_id=d.manufacturer_id))
    if m is not None:
        m = Manufacturer.query.get_or_404(m)
        form.manufacturer.data = m
    return render_template('admin/device.html', form=form)


@admin_blueprint.route('/device/<int:device_id>/delete', methods=['POST'])
def delete_device(device_id):
    d = Device.query.get_or_404(device_id).delete()
    flash(f"{d.name} erfolgreich gelöscht", "success")
    return jsonify(status='ok'), 201


@admin_blueprint.route('/device/<int:device_id>/edit', methods=['GET', 'POST'])
def edit_device(device_id):
    d = Device.query.get_or_404(device_id)
    form = EditDeviceForm(obj=d)
    if form.validate_on_submit():
        if Device.query.filter(Device.id != d.id, Device.name == form.name.data).first() is not None:
            form.name.errors.append("Es gibt bereits ein Gerät mit diesem Namen")
            return render_template('admin/device.html', form=form)
        d.name = form.name.data
        d.manufacturer = form.manufacturer.data
        d.picture = form.picture.data
        d.colors = form.colors.data
        d.save()
        flash(f"{d.name} erfolgreich aktualisiert", "success")
        return redirect(url_for('main.select_device', manufacturer_id=d.manufacturer_id))
    form.colors.data = d.colors
    return render_template('admin/device.html', form=form, manufacturer_id=d.manufacturer_id)


# REPAIRS

@admin_blueprint.route('/device/<int:device_id>/repair/add', methods=['GET'])
def add_repair(device_id):
    device = Device.query.get_or_404(device_id)
    device.repairs.append(Repair())
    db.session.commit()
    flash(f"Neue Reparatur zu {device.name} hinzugefügt", "success")
    return jsonify(status='ok'), 201


@admin_blueprint.route('/repair/<int:repair_id>/edit', methods=['GET', 'POST'])
def edit_repair(repair_id):
    r = Repair.query.get_or_404(repair_id)
    form = NewRepairForm(obj=r)
    if form.validate_on_submit():
        form.populate_obj(r)
        db.session.commit()
        flash(f"{r.name} wurde aktualisiert", "success")
        return jsonify(status='ok'), 201
    return render_template('admin/repair.html', form=form, repair_id=repair_id)


@admin_blueprint.route('/repair/<int:repair_id>/delete', methods=['POST'])
def delete_repair(repair_id):
    r = Repair.query.get_or_404(repair_id).delete()
    flash(f"{r.name} erfolgreich gelöscht", "success")
    return jsonify(status='ok'), 201


# COLORS


@admin_blueprint.route('/color/add', methods=['GET', 'POST'])
def add_color():
    form = NewColorForm()
    if form.validate_on_submit():
        c = Color.create(name=form.name.data, color_code=form.color_code.data)
        flash(f"{c.name} erfolgreich hinzugefügt", "success")
        return redirect(next_page())
    return render_template('admin/color.html', form=form)


@admin_blueprint.route('/color/<int:color_id>/delete', methods=['POST'])
def delete_color(color_id):
    pass


# SHOPS


@admin_blueprint.route('/shop/add', methods=['GET', 'POST'])
def add_shop():
    form = AddShopForm()
    if form.validate_on_submit():
        s = Shop.create(name=form.name.data)
        flash(f"{s.name} erfolgreich hinzugefügt", "success")
        return redirect(url_for('.add_shop'))
    return render_template('admin/panel/shops.html', form=form, shops=Shop.query.all())


@admin_blueprint.route('/shop/<string:shop_id>/delete', methods=['POST'])
def delete_shop(shop_id):
    s = Shop.query.get_or_404(shop_id).delete()
    flash(f"{s.name} erfolgreich gelöscht", "success")
    return jsonify(status='ok'), 201


# SETTINGS


@admin_blueprint.route('/settings/dashboard', methods=['GET', 'POST'])
def dashboard():
    page = request.args.get('page', 1, int)
    query = Enquiry.query.order_by(Enquiry.timestamp.desc())
    pagination = query.paginate(page, per_page=10, error_out=False)
    return render_template('admin/panel/dashboard.html',
                           sub_title="Dashboard",
                           pagination=pagination)


@admin_blueprint.route('/enquiry/<int:enquiry_id>/complete', methods=['POST'])
def complete_enquiry(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    enquiry.done = True
    enquiry.save()
    flash("Anfrage erfolgreich abgeschlossen.", 'success')
    return '', 200


@admin_blueprint.route('/settings/contactform', methods=['GET', 'POST'])
def contact_form_settings():
    p = Preferences.query.first()
    if p is None:
        Preferences.create()
        current_app.logger.warning('Missing preferences. Inserting default')

    form = ContactSettingsForm(obj=p)
    if form.validate_on_submit():
        form.populate_obj(p)
        db.session.commit()
        Preferences.load_settings()
        flash('Einstellungen erfolgreich angepasst', 'success')
        return redirect(url_for('.contact_form_settings'))
    return render_template('admin/panel/contactform.html',
                           form=form,
                           sub_title="Kontaktdaten")


@admin_blueprint.route('/settings/mail', methods=['GET', 'POST'])
def mail_settings():
    p = Preferences.query.first()
    if p is None:
        Preferences.create()
        current_app.logger.warning('Missing preferences. Inserting default')

    # Only the email form is validated in this function
    # The Test Form is validated in a separate function
    email_form = MailSettingsForm(obj=p)
    email_test_form = EmailTestForm()
    if email_form.validate_on_submit():
        p.mail_port = email_form.mail_port.data
        p.mail_server = email_form.mail_server.data
        p.mail_default_sender = email_form.mail_default_sender.data
        p.mail_encryption = email_form.mail_encryption.data
        p.mail_username = email_form.mail_username.data
        p.order_copy_mail_address = email_form.order_copy_mail_address.data
        if email_form.mail_password.data and len(email_form.mail_password.data) > 0:
            p.encrypt_mail_password(email_form.mail_password.data)
        p.save()
        flash('Einstellungen erfolgreich angepasst', 'success')
        return redirect(url_for('.mail_settings'))
    return render_template('admin/panel/mailsettings.html',
                           form=email_form,
                           sub_title="Mail Einstellungen",
                           email_test_form=email_test_form)


@admin_blueprint.route('/settings/password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        current_user.save()
        flash('Passwort erfolgreich geändert.', 'success')
        logout_user()
        return redirect(url_for('main.home'))
    return render_template('admin/panel/password.html',
                           form=form,
                           sub_title="Passwort ändern")


@admin_blueprint.route('/settings/import', methods=['GET', 'POST'])
def import_csv():
    form = CsvUploadForm()
    if form.validate_on_submit():
        importer = RepairCsvImporter(form.csv.data)
        importer.import_csv()

    return render_template('admin/panel/import.html',
                           form=form,
                           sub_title="Reparaturdaten importieren")


@admin_blueprint.route('/mail/test', methods=['POST'])
def send_test_mail():
    email_test_form = EmailTestForm()
    if email_test_form.validate_on_submit():
        current_app.logger.debug(f"Sending Test Mail to {email_test_form.recipient.data}.")
        send_email_task.apply_async((TestEmail(recipients=email_test_form.recipient.data).__dict__,))
        flash("Email wurde erfolgreich versandt.", "success")
        return jsonify({"status": "success"}), 201
    return render_template('admin/panel/test_mail_form.html',
                           email_test_form=email_test_form
                           )


@admin_blueprint.route('/settings/sale', methods=['GET', 'POST'])
def configure_sale():
    p = Preferences.query.first()
    form = SaleForm(obj=p)
    if form.validate_on_submit():
        form.populate_obj(p)
        db.session.commit()
        flash("Einstellungen erfolgreich aktualisiert", "success")
        return redirect(url_for('.configure_sale'))
    return render_template('admin/panel/configure_sale.html', form=form, sub_title="Sale")


# Stats
@admin_blueprint.route('/stats', methods=['GET', 'POST'])
def stats():
    page = request.args.get('page', 1, int)
    from price_picker.analytics import SORTED_SESSION_LIST, TOP_LIST, first_or_none
    total = analytics.redis.zcard(SORTED_SESSION_LIST)
    now = dt.datetime.now().timestamp()
    start = now - 86400
    total_24 = analytics.redis.zcount(SORTED_SESSION_LIST, int(start), int(now))
    top_page = first_or_none(analytics.redis.zrange(TOP_LIST, 0, 0))

    pagination = analytics.get_visits_paginated(page, 10)
    return render_template('admin/panel/stats.html',
                           sub_title='Stats',
                           total=total,
                           total_24=total_24,
                           top_page=top_page.decode('utf-8') if top_page else '-',
                           pagination=pagination)


# WHEEL OF FORTUNE

@admin_blueprint.route('/wof/list', methods=['GET'])
def wof_list_mails():
    page = request.args.get('page', 1, int)
    query = Mail.query
    pagination = query.paginate(page, per_page=10, error_out=False)
    return render_template('admin/panel/mails.html',
                           sub_title="Mails",
                           pagination=pagination)
