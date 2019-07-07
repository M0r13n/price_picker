from price_picker import db
from price_picker.common.database import CRUDMixin
from sqlalchemy.orm import relationship

PICTURE_BASE_PATH = "device_mocks/"


class Picture(db.Model):
    """
    All pictures are stored in a html subpage inside the device_mocks folder.
    There is also a default one.
    """
    __tablename__ = 'pictures'
    name = db.Column(db.String(64), unique=True, primary_key=True, nullable=False)
    filename = db.Column(db.String(128), unique=True, nullable=False)
    default = db.Column(db.Boolean, default=False, index=True)
    manufacturers = db.relationship('Manufacturer', backref='picture')
    devices = db.relationship('Device', backref='picture')

    def __repr__(self):
        return f"<Picture {self.name}@[{self.file}]"

    @classmethod
    def query_factory_all(cls):
        """
        Query Factory for use in sqlalchemy.wtforms
        """
        return cls.query.order_by(cls.name)

    @property
    def dir(self):
        return PICTURE_BASE_PATH

    @property
    def file(self):
        return f"{self.dir}{self.filename}"

    @classmethod
    def default_picture(cls):
        return cls.query.filter_by(default=True).first()

    @staticmethod
    def create_basic_pictures():
        """
        Insert default Pictures and set the default
        :return:
        """
        basics = {
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
        # set default picture
        default = 'nexus'
        for k, v in basics.items():
            p = Picture.query.filter_by(name=k).first()
            if p is None:
                p = Picture(name=k, filename=v, default=k == default)
            db.session.add(p)
            db.session.commit()


class Manufacturer(db.Model, CRUDMixin):
    __tablename__ = 'manufacturers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    devices = relationship('Device', back_populates='manufacturer', cascade="all, delete-orphan")
    picture_id = db.Column(db.String, db.ForeignKey('pictures.name'))

    def __init__(self, **kwargs):
        super(Manufacturer, self).__init__(**kwargs)
        if self.picture is None:
            self.picture = Picture.default_picture()
            print(self.picture)

    @property
    def picture_file(self):
        if self.picture is None:
            return Picture.default_picture().file
        return self.picture.file

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

color_association_table = db.Table('color_association',
                                   db.Column('device_id', db.Integer, db.ForeignKey('devices.id', ondelete="cascade")),
                                   db.Column('color_name', db.String, db.ForeignKey('color.name', ondelete="cascade"))
                                   )


class Device(db.Model, CRUDMixin):
    """
    Generic Device
    Can be a Smartphone, Tablet or anything else
    """
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturers.id'))
    manufacturer = relationship('Manufacturer', back_populates='devices')
    repairs = relationship('Repair', secondary=repair_association_table, back_populates='devices', lazy='dynamic')
    picture_id = db.Column(db.String, db.ForeignKey('pictures.name'))
    colors = relationship("Color", secondary=color_association_table)

    def __init__(self, **kwargs):
        super(Device, self).__init__(**kwargs)
        if len(self.colors) == 0:
            default_color = Color.query.filter_by(default=True).first()
            if default_color is not None:
                self.colors.append(default_color)

    def __repr__(self):
        return f"<Device: {self.manufacturer.name} - {self.name}>"

    @property
    def picture_file(self):
        """
        Get the picture file or if none is provided use the manufacturers default
        and if no picture is defined at all it uses the default picture.
        :return: template path of associated html render
        """
        if self.picture is None:
            return self.manufacturer.picture_file
        return self.picture.file

    @classmethod
    def query_factory_all(cls):
        """
        Query Factory for use in sqlalchemy.wtforms
        """
        return cls.query.order_by(cls.name)

    @classmethod
    def _check_if_paths_are_valid(cls):
        """
        private function to ensure every device points to a html render
        :return: True if everything is valid else False
        """
        for d in cls.query.all():
            if d.picture is None or d.picture_file is None:
                return False
        return True


class Repair(db.Model, CRUDMixin):
    """ Repair e.g. display """
    __tablename__ = 'repair'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    price = db.Column(db.Integer, default=0)
    devices = relationship("Device", secondary=repair_association_table, back_populates="repairs", lazy='dynamic')

    def __repr__(self):
        return f"<{self.name} : {self.price}"


class Color(db.Model, CRUDMixin):
    """ Store colors and their associated color codes """
    __tablename__ = 'color'
    name = db.Column(db.String(128), primary_key=True)
    color_code = db.Column(db.String(20))
    default = db.Column(db.Boolean, default=False, index=True)

    @classmethod
    def query_factory_all(cls):
        """
        Query Factory for use in sqlalchemy.wtforms
        """
        return cls.query.order_by(cls.name)

    def __repr__(self):
        return f"<{self.name} : {self.color_code}>"
