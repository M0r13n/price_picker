import unittest

from tests.base import BaseTestCase
from price_picker.models import Manufacturer, Device, Preferences, Enquiry
from price_picker import db


class TestMainBlueprint(BaseTestCase):
    def test_404(self):
        # Ensure 404 error is handled.
        response = self.client.get("/404")
        self.assert404(response)
        self.assertTemplateUsed("errors/404.html")

    def test_index(self):
        # Ensure Flask is setup.
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Wie lautet der Hersteller", response.data)

    def test_select_device(self):
        # Normal
        apple = Manufacturer.query.filter(Manufacturer.name == "Apple").first()
        self.assertIsNotNone(apple)
        response = self.client.get(f"/manufacturer/{apple.id}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Gerät wählen".encode('utf-8'), response.data)
        self.assertIn("iPhone 5".encode('utf-8'), response.data)
        self.assertIn("iPhone X".encode('utf-8'), response.data)

        # Ensure 404 error is thrown in invalid manufacturer
        response = self.client.get(f"/manufacturer/{347345439587}", follow_redirects=True)
        self.assert404(response)
        self.assertTemplateUsed("errors/404.html")

    def test_select_color(self):
        device = Device.query.filter(Device.name == "iPhone 7").first()
        self.assertIsNotNone(device)
        response = self.client.get(f"/device/{device.id}/color", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("black".encode('utf-8'), response.data)
        self.assertIn("white".encode('utf-8'), response.data)

        # Ensure 404 error is thrown in invalid device
        response = self.client.get(f"/device/{347345439587}/color", follow_redirects=True)
        self.assert404(response)
        self.assertTemplateUsed("errors/404.html")

    def test_select_repair(self):
        device = Device.query.filter(Device.name == "iPhone 7").first()
        response = self.client.get(f"/device/{device.id}", follow_redirects=True)
        repairs = device.repairs
        # assert all repairs are listed
        for repair in repairs:
            self.assertIn(repair.name.encode('utf-8'), response.data)
        # assert sonstige is listed
        self.assertIn("sonstige".encode('utf-8'), response.data)

    def test_completion(self):
        device = Device.query.filter(Device.name == "iPhone 7").first()
        response = self.client.get(f"/complete/{device.id}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        p = Preferences.query.first()

        # GET
        self.assertIn("imei".encode('utf-8'), response.data)
        self.assertIn("Telefonnummer".encode('utf-8'), response.data)
        self.assertIn("mail".encode('utf-8'), response.data)
        self.assertIn("first_name".encode('utf-8'), response.data)
        self.assertIn("last_name".encode('utf-8'), response.data)
        self.assertNotIn("Straße".encode('utf-8'), response.data)
        self.assertNotIn("Haus".encode('utf-8'), response.data)
        self.assertNotIn("is-invalid".encode('utf-8'), response.data)

        # POST
        # wrong
        with self.client:
            response = self.client.post(
                f"/complete/{device.id}",
                data=dict(last_name="LASTNAME"),
                follow_redirects=True,
            )
            self.assertTemplateUsed("main/complete.html")
            self.assertIn("is-invalid".encode('utf-8'), response.data)

        # right
        with self.client:
            with self.client.session_transaction() as sess:
                sess['repair_ids'] = [1, 2, 3]
            response = self.client.post(
                f"/complete/{device.id}",
                data=dict(email="e@mail.com"),
                follow_redirects=True,
            )
            self.assertIn("Vielen Dank".encode('utf-8'), response.data)
            self.assertTemplateUsed("main/thank_you.html")

        p.address_required = True
        db.session.commit()
        p.load_settings()

        # GET

        response = self.client.get(f"/complete/{device.id}", follow_redirects=True)
        self.assertIn("imei".encode('utf-8'), response.data)
        self.assertIn("Telefonnummer".encode('utf-8'), response.data)
        self.assertIn("mail".encode('utf-8'), response.data)
        self.assertIn("first_name".encode('utf-8'), response.data)
        self.assertIn("last_name".encode('utf-8'), response.data)
        self.assertIn("Straße".encode('utf-8'), response.data)
        self.assertIn("Haus".encode('utf-8'), response.data)

        # Test invalid Feedback

        def post_data(data):
            with self.client:
                with self.client.session_transaction() as sess:
                    sess['repair_ids'] = [1, 2, 3]
                return self.client.post(
                    f"/complete/{device.id}",
                    data=data,
                    follow_redirects=True,
                )

        response = post_data(dict(first_name="A" * 64))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Max 60 Zeichen".encode('utf-8'), response.data)

        response = post_data(dict(last_name="A" * 64))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Max 60 Zeichen".encode('utf-8'), response.data)

        response = post_data(dict(email="A" * 128))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Max 120 Zeichen".encode('utf-8'), response.data)

        response = post_data(dict(email="A"))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("gültig".encode('utf-8'), response.data)

        response = post_data(dict(phone="A" * 60))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Die Telefonnummer ist nicht gültig".encode('utf-8'), response.data)

        response = post_data(dict(imei="A" * 60))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Die IMEI kann maximal 40 Zeichen enthalten".encode('utf-8'), response.data)

        response = post_data(dict(customer_street="A" * 129))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Max 128 Zeichen".encode('utf-8'), response.data)

        response = post_data(dict(customer_postal_code="A" * 33))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Max 32 Zeichen".encode('utf-8'), response.data)

        response = post_data(dict(customer_city="A" * 129))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("Max 128 Zeichen".encode('utf-8'), response.data)

        response = post_data(dict(customer_city="A", customer_street="AA", phone="1212", first_name="ffff", last_name="dsfsdf"))
        self.assertTemplateUsed("main/complete.html")
        self.assertIn("is-invalid".encode('utf-8'), response.data)
        self.assertIn("benötigt".encode('utf-8'), response.data)

        # post
        Enquiry.query.delete()
        db.session.commit()
        response = post_data(
            dict(customer_city="A", email="e@mail.io", customer_street="AA", phone="1212", first_name="ffff", last_name="dsfsdf"))
        e = Enquiry.query.first()
        self.assertIsNotNone(e)
        self.assertTrue(e.customer_email == "e@mail.io")
        self.assertTrue(e.customer_city == "A")
        self.assertTrue(e.customer_street == "AA")
        self.assertTrue(e.customer_phone == "1212")
        self.assertTrue(e.customer_first_name == "ffff")
        self.assertTrue(e.customer_last_name == "dsfsdf")

        # post without repair ids
        with self.client:
            with self.client.session_transaction() as sess:
                sess['repair_ids'] = None
            response = self.client.post(
                f"/complete/{device.id}",
                data=dict(customer_city="A", email="e@mail.io", customer_street="AA", phone="1212", first_name="ffff", last_name="dsfsdf"),
                follow_redirects=True,
            )
        self.assertTemplateUsed("main/select_repair.html")
        self.assertIn("erneut".encode('utf-8'), response.data)


if __name__ == "__main__":
    unittest.main()
