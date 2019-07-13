# project/server/tests/base.py


from flask_testing import TestCase

from price_picker import db, create_app
from price_picker.common.create_sample_data import create_sample_data

app = create_app()


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object("config.TestingConfig")
        return app

    def setUp(self):
        db.create_all()
        create_sample_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
