from price_picker import db

from sqlalchemy.orm import relationship

CSS_PATHS = {
    'Apple': '_iphone_8.html',
    'Samsung': '_s5.html',
    'HTC': '_htc.html'
}


class Manufacturer(db.Model):
    __tablename__ = 'manufacturers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    devices = relationship("Device", back_populates="manufacturer")

    def __repr__(self):
        return f"<Manufacturer: {self.name}>"

    @classmethod
    def query_factory_all(cls):
        """
        Query Factory for use in sqlalchemy.wtforms
        """
        return cls.query.order_by(cls.name)


class Device(db.Model):
    """
    Generic Device
    Can be a Smartphone, Tablet or anything else
    """
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id'))
    manufacturer = relationship("Manufacturer", back_populates="devices")
    css_img_name = db.Column(db.String(128), default="_nexus_5.html")

    def __init__(self, **kwargs):
        super(Device, self).__init__(**kwargs)
        if self.css_img_name is None:
            self.css_img_name = CSS_PATHS.get(self.manufacturer.name)

    def __repr__(self):
        return f"<Device: {self.manufacturer.name} - {self.name}>"

    @property
    def css_path(self):
        return f'device_mocks/{self.css_img_name}'

    @classmethod
    def query_factory_all(cls):
        """
        Query Factory for use in sqlalchemy.wtforms
        """
        return cls.query.order_by(cls.name)
