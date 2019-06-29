from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import current_user
from .forms import NewDeviceForm, EditDeviceForm, NewManufacturerForm, EditManufacturerForm, DeleteForm, NewRepairForm
from price_picker.models import Device, Manufacturer, Repair
from price_picker import db
from price_picker.common.next_page import next_page

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.before_request
def require_login():
    if not current_user.is_authenticated:
        flash('Dieser Bereich erfordert einen Login!', 'danger')
        return redirect(url_for('main.login', next=request.full_path))


@admin_blueprint.route('/manufacturer/add', methods=['GET', 'POST'])
def add_manufacturer():
    form = NewManufacturerForm()
    if form.validate_on_submit():
        m = Manufacturer(name=form.name.data, picture=form.picture.data)
        db.session.add(m)
        db.session.commit()
        flash(f"{m.name} erfolgreich hinzugefügt", "success")
        return redirect(next_page())
    return render_template('admin/add_manufacturer.html', form=form)


@admin_blueprint.route('/manufacturer/<int:manufacturer_id>/delete', methods=['DELETE', 'POST'])
def delete_manufacturer(manufacturer_id):
    form = DeleteForm()
    if form.validate_on_submit():
        m = Manufacturer.query.get_or_404(manufacturer_id)
        name = m.name
        db.session.delete(m)
        db.session.commit()
        flash(f"{name} erfolgreich gelöscht", "success")
        return redirect(url_for('main.home'))


@admin_blueprint.route('/manufacturer/<int:manufacturer_id>/edit', methods=['GET', 'POST'])
def edit_manufacturer(manufacturer_id):
    m = Manufacturer.query.get_or_404(manufacturer_id)
    form = EditManufacturerForm(obj=m)
    if form.validate_on_submit():
        if Manufacturer.query.filter(Manufacturer.id != m.id, Manufacturer.name == form.name.data).first() is not None:
            form.name.errors.append("Es gibt bereits ein Hersteller mit diesem Namen")
            return render_template('admin/add_manufacturer.html', form=form)
        m.name = form.name.data
        m.picture = form.picture.data
        db.session.commit()
        flash(f"{m.name} erfolgreich aktualisiert", "success")
        return redirect(url_for('main.home'))
    return render_template('admin/add_manufacturer.html', form=form)


@admin_blueprint.route('/device/add', methods=['GET', 'POST'])
def add_device():
    m = request.args.get('manufacturer_id', None, int)
    form = NewDeviceForm()
    if form.validate_on_submit():
        d = Device(name=form.name.data, manufacturer=form.manufacturer.data, picture=form.picture.data)
        db.session.add(d)
        db.session.commit()
        flash(f"{d.name} erfolgreich hinzugefügt", "success")
        return redirect(url_for('main.select_device', manufacturer_id=d.manufacturer_id))
    if m is not None:
        m = Manufacturer.query.get_or_404(m)
        form.manufacturer.data = m
    return render_template('admin/add_device.html', form=form)


@admin_blueprint.route('/device/<int:device_id>/delete', methods=['DELETE', 'POST'])
def delete_device(device_id):
    form = DeleteForm()
    if form.validate_on_submit():
        d = Device.query.get_or_404(device_id)
        name, m_id = d.name, d.manufacturer_id
        db.session.delete(d)
        db.session.commit()
        flash(f"{name} erfolgreich gelöscht", "success")
        return redirect(url_for('main.select_device', manufacturer_id=m_id))


@admin_blueprint.route('/device/<int:device_id>/edit', methods=['GET', 'POST'])
def edit_device(device_id):
    d = Device.query.get_or_404(device_id)
    form = EditDeviceForm(obj=d)
    if form.validate_on_submit():
        if Device.query.filter(Device.id != d.id, Device.name == form.name.data).first() is not None:
            form.name.errors.append("Es gibt bereits ein Gerät mit diesem Namen")
            return render_template('admin/add_device.html', form=form)
        d.name = form.name.data
        d.manufacturer = form.manufacturer.data
        d.picture = form.picture.data
        db.session.commit()
        flash(f"{d.name} erfolgreich aktualisiert", "success")
        return redirect(url_for('main.select_device', manufacturer_id=d.manufacturer_id))
    return render_template('admin/add_device.html', form=form)


@admin_blueprint.route('/device/<int:device_id>/repair/add', methods=['GET', 'POST'])
def add_repair(device_id):
    device = Device.query.get_or_404(device_id)
    form = NewRepairForm()
    if form.validate_on_submit():
        r = Repair()
        form.populate_obj(r)
        device.repairs.append(r)
        db.session.commit()
        flash(f"{r.name} erfolgreich zu {device.name} hinzugefügt", "success")
        return redirect(url_for('main.select_repair', device_id=device_id))
    return render_template('admin/add_repair.html', form=form, device=device)


@admin_blueprint.route('/repair/<int:repair_id>/edit', methods=['GET', 'POST'])
def edit_repair(repair_id):
    r = Repair.query.get_or_404(repair_id)
    form = NewRepairForm(obj=r)
    if form.validate_on_submit():
        form.populate_obj(r)
        db.session.commit()
        flash(f"{r.name} wurde aktualisiert", "success")
        return redirect(url_for('main.select_repair', device_id=r.devices.first().id))
    return render_template('admin/add_repair.html', form=form, device=r.devices.first())


@admin_blueprint.route('/repair/<int:repair_id>/delete', methods=['DELETE', 'POST'])
def delete_repair(repair_id):
    form = DeleteForm()
    if form.validate_on_submit():
        r = Repair.query.get_or_404(repair_id)
        name = r.name
        db.session.delete(r)
        db.session.commit()
        flash(f"{name} erfolgreich gelöscht", "success")
        return redirect(url_for('main.home'))
