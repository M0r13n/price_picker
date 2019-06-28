from flask import Blueprint, redirect, url_for, flash, request
from flask_login import current_user

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.before_request
def require_login():
    if not current_user.is_authenticated:
        flash('Dieser Bereich erfordert einen Login!', 'danger')
        return redirect(url_for('main.login', next=request.full_path))


@admin_blueprint.route('/manufacturer/add', methods=['GET', 'POST'])
def add_manufacturer():
    return ""


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
