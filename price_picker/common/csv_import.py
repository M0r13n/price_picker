from io import TextIOWrapper
import csv
from price_picker.models import Manufacturer, Device, Repair
from price_picker import db
from flask import has_app_context


def _secure_file(csv_file, encoding='utf-8'):
    csv_file = TextIOWrapper(csv_file, encoding=encoding)
    return csv_file


class CsvImporter(object):
    def __init__(self, csv_file, delimiter=','):
        self.csv_file = _secure_file(csv_file)
        self.delimiter = delimiter
        self.csv_reader = csv.reader(self.csv_file, delimiter=self.delimiter)

    def import_csv(self):
        raise NotImplementedError("This method should be overwritten!")


class RepairCsvImporter(CsvImporter):
    """
     A csv importer for Repairs

     Format must be [Manufacturer-Name , Device-Name , Repair-Name, Price]
    """

    def __init__(self, *args, **kwargs):
        self.min_cols = 4
        super().__init__(*args, **kwargs)

    def import_csv(self):
        if not has_app_context():
            # todo custom exception
            return None

        for row in self.csv_reader:

            if len(row) < self.min_cols:
                # todo custom exception
                continue

            manufacturer_name, device_name, repair_name, price = row

            # Get manufacturer
            manufacturer = Manufacturer.query.filter(Manufacturer.name == manufacturer_name).first()
            if manufacturer is None:
                manufacturer = Manufacturer(name=manufacturer_name)
                db.session.add(manufacturer)

            # Get device
            device = Device.query.filter(Device.name == device_name).first()
            if device is None:
                device = Device(name=device_name, manufacturer=manufacturer)
                db.session.add(device)

            # Get repair
            repair = device.repairs.filter(Repair.name == repair_name).first()
            if repair is None:
                device.repairs.append(Repair(name=repair_name, price=price))
            else:
                repair.price = price

        db.session.commit()
