from price_picker.common.database import CRUDMixin
from price_picker import db


class Shop(CRUDMixin, db.Model):
    """ Shops """
    __tablename__ = 'shops'
    name = db.Column(db.String(128), primary_key=True, unique=True, default="Zentrale")

    @classmethod
    def query_factory_all(cls):
        # insert default if no shop exists
        if cls.query.first() is None:
            cls.create()
        return cls.query.order_by(cls.name)

    def __str__(self):
        return self.name

    __repr__ = __str__
