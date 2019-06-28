from flask import render_template, Blueprint
from price_picker.models import Manufacturer, Device

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def home():
    manufacturers = Manufacturer.query.order_by(Manufacturer.name).all()
    return render_template("main/home.html",
                           manufacturers=manufacturers)


@main_blueprint.route("/manufacturer/<int:manufacturer_id>")
def select_device(manufacturer_id):
    devices = Device.query.filter(Device.manufacturer_id == manufacturer_id).all()
    return render_template("main/select_device.html", devices=devices)


@main_blueprint.route("/device/<int:device_id>")
def select_repair(device_id):
    device = Device.query.get_or_404(device_id)
    return render_template('main/select_repair.html', device=device)
