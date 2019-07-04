# manage.py


import unittest

import coverage

from flask.cli import FlaskGroup
from price_picker import create_app, db
from price_picker.models import User, Device, Manufacturer, Repair, Picture, Color, Preferences
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
    Repair.query.delete()
    Picture.query.delete()
    User.query.delete()
    Color.query.delete()
    Preferences.query.delete()

    # default preferences
    db.session.add(Preferences())

    # some colors
    black = Color(name="black", color_code="#000000")
    white = Color(name="white", color_code="#FFFFFF")
    gold = Color(name="gold", color_code="#D4AF37")
    db.session.add(black)
    db.session.add(white)
    db.session.add(gold)

    db.session.add(User(username="admin", password="admin"))
    Picture.create_basic_pictures()

    apple = Manufacturer(name="Apple", picture=Picture.query.filter_by(name='iphone_x').first())
    samsung = Manufacturer(name="Samsung", picture=Picture.query.filter_by(name='s5').first())
    huawei = Manufacturer(name="Huawei", picture=Picture.query.filter_by(name='note').first())
    htc = Manufacturer(name='HTC', picture=Picture.query.filter_by(name='htc').first())
    oneplus = Manufacturer(name='OnePlus')
    db.session.add(htc)
    db.session.add(samsung)
    db.session.add(huawei)
    db.session.add(oneplus)

    ip4 = Device(name="iPhone 4", manufacturer=apple, colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_4s').first())
    ip5 = Device(name="iPhone 5", manufacturer=apple, colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_5s').first())
    ip5s = Device(name="iPhone 5s", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_5s').first())
    ip5c = Device(name="iPhone 5c", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_5c').first())
    ip6 = Device(name="iPhone 6", manufacturer=apple, colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_8').first())
    ip6p = Device(name="iPhone 6 Plus", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_8_plus').first())
    ip6s = Device(name="iPhone 6s", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_8').first())
    ip6sp = Device(name="iPhone 6s Plus", manufacturer=apple, colors=[black, white],
                   picture=Picture.query.filter_by(name='iphone_8_plus').first())
    ip7 = Device(name="iPhone 7", manufacturer=apple, colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_8').first())
    ip7p = Device(name="iPhone 7 Plus", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_8_plus').first())
    ip8 = Device(name="iPhone 8", manufacturer=apple, colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_x').first())
    ip8p = Device(name="iPhone 8 Plus", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_x').first())
    ipx = Device(name="iPhone X", manufacturer=apple, colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_x').first())
    ipxs = Device(name="iPhone Xs", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_x').first())
    ipxsm = Device(name="iPhone Xs Max", manufacturer=apple, colors=[black, white],
                   picture=Picture.query.filter_by(name='iphone_x').first())
    ipxr = Device(name="iPhone Xr", manufacturer=apple, colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_x').first())
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
    if not Device._check_if_paths_are_valid():
        raise ValueError('Some devices have undefined picture paths')
    print('Successfully added sample data')


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
