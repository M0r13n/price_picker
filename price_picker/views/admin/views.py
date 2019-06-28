from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import current_user
from .forms import NewDeviceForm, EditDeviceForm, NewManufacturerForm, EditManufacturerForm
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
        m = Manufacturer()
        form.populate_obj(m)
        db.session.add(m)
        db.session.commit()
        flash(f"{m.name} erfolgreich hinzugefügt", "success")
        return redirect(url_for('main.home'))
    return render_template('admin/add_manufacturer.html', form=form)


@admin_blueprint.route('/manufacturer/delete', methods=['DELETE', 'POST'])
def delete_manufacturer():
    pass


@admin_blueprint.route('/manufacturer/edit', methods=['GET', 'POST'])
def edit_manufacturer():
    pass


@admin_blueprint.route('/device/add', methods=['GET', 'POST'])
def add_device():
    pass


@admin_blueprint.route('/device/delete', methods=['DELETE', 'POST'])
def delete_device():
    pass


@admin_blueprint.route('/device/edit', methods=['GET', 'POST'])
def edit_device():
    pass


@admin_blueprint.route('/device/<int:device_id>/repair/list', methods=['GET', 'POST'])
def list_repairs(device_id):
    pass


@admin_blueprint.route('/device/<int:device_id>/repair/add', methods=['GET', 'POST'])
def add_repair(device_id):
    pass


@admin_blueprint.route('/device/<int:device_id>/repair/delete', methods=['DELETE', 'POST'])
def delete_repair(device_id):
    pass
