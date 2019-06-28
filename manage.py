# manage.py


import unittest

import coverage

from flask.cli import FlaskGroup
from price_picker import create_app, db
from price_picker.models import User
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
    pass


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
