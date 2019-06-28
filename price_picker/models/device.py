from price_picker import db

from sqlalchemy.orm import relationship

CSS_RENDER_PATHS = {
    'htc': '_htc.html',
    'ipad': '_ipad_mini.html',
    'iphone_4s': '_iphone_4s.html',
    'iphone_5s': '_iphone_5s.html',
    'iphone_5c': '_iphone_5c.html',
    'iphone_8': '_iphone_8.html',
    'iphone_8_plus': '_iphone_8_plus.html',
    'iphone_x': '_iphone_x.html',
    'nexus': '_nexus_5.html',
    'note': '_note_8.html',
    's5': '_s5.html',
}


class Manufacturer(db.Model):
    __tablename__ = 'manufacturers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    devices = relationship("Device", back_populates="manufacturer")
    css_img_name = db.Column(db.String(128), default=CSS_RENDER_PATHS['nexus'])

    def __repr__(self):
        return f"<Manufacturer: {self.name}>"

    @property
    def css_path(self):
        return f'device_mocks/{self.css_img_name}'

    @classmethod
    def query_factory_all(cls):
        """
        Query Factory for use in sqlalchemy.wtforms
        """
        return cls.query.order_by(cls.name)


repair_association_table = db.Table('repair_association',
                                    db.Column('device_id', db.Integer, db.ForeignKey('devices.id', ondelete="cascade")),
                                    db.Column('repair_id', db.Integer, db.ForeignKey('repair.id', ondelete="cascade"))
                                    )


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
    css_img_name = db.Column(db.String(128))
    repairs = relationship("Repair", secondary=repair_association_table, back_populates="devices")

    def __repr__(self):
        return f"<Device: {self.manufacturer.name} - {self.name}>"

    @property
    def css_path(self):
        img_name = self.css_img_name
        if img_name is None:
            img_name = self.manufacturer.css_img_name or CSS_RENDER_PATHS['nexus']
        return f'device_mocks/{img_name}'

    @classmethod
    def query_factory_all(cls):
        """
        Query Factory for use in sqlalchemy.wtforms
        """
        return cls.query.order_by(cls.name)


class Repair(db.Model):
    """ Repair e.g. display """
    __tablename__ = 'repair'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    price = db.Column(db.Integer)
    devices = relationship("Device", secondary=repair_association_table, back_populates="repairs", lazy='dynamic')
