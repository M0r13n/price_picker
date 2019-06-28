# manage.py


import unittest

import coverage

from flask.cli import FlaskGroup
from price_picker import create_app, db
from price_picker.models import User, Device, Manufacturer, Repair
import subprocess
import sys

app = create_app()
cli = FlaskGroup(create_app=create_app)

# code coverage
COV = coverage.coverage(
    branch=True,
    include="price_picker/*",
    omit=[
        "price_picker/tests/*",
        "price_picker/server/config.py",
        "price_picker/server/*/__init__.py",
    ],
)
COV.start()


@cli.command()
def create_db():
    print('Dropping DB.')
    db.drop_all()
    print('Creating Tables.')
    db.create_all()
    print('Database created successfully.')
    db.session.commit()


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command()
def create_admin():
    """Creates the admin user."""
    db.session.add(User(username="admin", password="admin"))
    print('Admin added successfully.')
    db.session.commit()


@cli.command()
def create_data():
    """Creates sample data."""
    print("Adding Sample Data")
    Device.query.delete()
    Manufacturer.query.delete()

    apple = Manufacturer(name="Apple", css_img_name="_iphone_x.html")
    samsung = Manufacturer(name="Samsung", css_img_name="_s5.html")
    huawei = Manufacturer(name="Huawei")
    htc = Manufacturer(name='HTC', css_img_name="_htc.html")
    oneplus = Manufacturer(name='OnePlus', css_img_name="_note_8.html")
    db.session.add(htc)
    db.session.add(samsung)
    db.session.add(huawei)
    db.session.add(oneplus)

    ip4 = Device(name="iPhone 4", manufacturer=apple, css_img_name="_iphone_4s.html")
    ip5 = Device(name="iPhone 5", manufacturer=apple, css_img_name="_iphone_5s.html")
    ip5s = Device(name="iPhone 5s", manufacturer=apple, css_img_name="_iphone_5s.html")
    ip5c = Device(name="iPhone 5c", manufacturer=apple, css_img_name="_iphone_5c.html")
    ip6 = Device(name="iPhone 6", manufacturer=apple, css_img_name="_iphone_8.html")
    ip6p = Device(name="iPhone 6 Plus", manufacturer=apple, css_img_name="_iphone_8_plus.html")
    ip6s = Device(name="iPhone 6s", manufacturer=apple, css_img_name="_iphone_8.html")
    ip6sp = Device(name="iPhone 6s Plus", manufacturer=apple, css_img_name="_iphone_8_plus.html")
    ip7 = Device(name="iPhone 7", manufacturer=apple, css_img_name="_iphone_8.html")
    ip7p = Device(name="iPhone 7 Plus", manufacturer=apple, css_img_name="_iphone_8_plus.html")
    ip8 = Device(name="iPhone 8", manufacturer=apple, css_img_name="_iphone_8.html")
    ip8p = Device(name="iPhone 8 Plus", manufacturer=apple, css_img_name="_iphone_8_plus.html")
    ipx = Device(name="iPhone X", manufacturer=apple, css_img_name="_iphone_x.html")
    ipxs = Device(name="iPhone Xs", manufacturer=apple, css_img_name="_iphone_x.html")
    ipxsm = Device(name="iPhone Xs Max", manufacturer=apple, css_img_name="_iphone_x.html")
    ipxr = Device(name="iPhone Xr", manufacturer=apple, css_img_name="_iphone_x.html")
    db.session.add(ip4)
    db.session.add(ip5)
    db.session.add(ip7p)
    db.session.add(ip7)
    db.session.add(ipx)
    db.session.add(ip8)
    db.session.add(ip5s)
    db.session.add(ip5c)
    db.session.add(ip6)
    db.session.add(ip6p)
    db.session.add(ip6s)
    db.session.add(ip6sp)
    db.session.add(ip8p)
    db.session.add(ipxs)
    db.session.add(ipxsm)
    db.session.add(ipxr)

    # some repairs
    ipx.repairs.append(Repair(name="Display", price=429))
    ipx.repairs.append(Repair(name="Akku", price=129))
    ipx.repairs.append(Repair(name="Backcover", price=379))
    ipx.repairs.append(Repair(name="Kleinteil", price=150))

    db.session.commit()


@cli.command()
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover("price_picker/tests", pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover("price_picker/tests")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print("Coverage Summary:")
        COV.report()
        COV.html_report()
        COV.erase()
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def flake():
    """Runs flake8 on the price_picker."""
    subprocess.run(["flake8", "price_picker"])


if __name__ == "__main__":
    cli()
