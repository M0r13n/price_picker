from price_picker.models import User, Device, Manufacturer, Repair, Picture, Color, Preferences, Enquiry
from price_picker import db


def create_sample_data():
    """Creates sample data."""
    print("Adding Sample Data")
    # Delete all data
    Enquiry.query.delete()
    Device.query.delete()
    Manufacturer.query.delete()
    Repair.query.delete()
    Picture.query.delete()
    User.query.delete()
    Color.query.delete()
    Preferences.query.delete()

    # Insert default preferences
    db.session.add(Preferences())

    # Insert admin
    db.session.add(User(username="admin", password="admin"))

    # Insert default Pictures
    Picture.create_basic_pictures()

    # Insert default colors
    black = Color(name="black", color_code="#000000", default=True)
    white = Color(name="white", color_code="#FFFFFF")
    gold = Color(name="gold", color_code="#D4AF37")
    db.session.add(black)
    db.session.add(white)
    db.session.add(gold)

    # Insert default manufacturers
    apple = Manufacturer(name="Apple", picture=Picture.query.filter_by(name='iphone_x').first())
    samsung = Manufacturer(name="Samsung", picture=Picture.query.filter_by(name='s5').first())
    huawei = Manufacturer(name="Huawei", picture=Picture.query.filter_by(name='note').first())
    htc = Manufacturer(name='HTC', picture=Picture.query.filter_by(name='htc').first())
    oneplus = Manufacturer(name='OnePlus')
    db.session.add(htc)
    db.session.add(samsung)
    db.session.add(huawei)
    db.session.add(oneplus)

    # Apple
    ip4 = Device(name="iPhone 4",
                 manufacturer=apple,
                 colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_4s').first(),
                 repairs=[Repair(name="Display", price=69), Repair(name="Akku", price=30), Repair(name="Kleinteil", price=45)])

    ip4s = Device(name="iPhone 4S",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_4s').first(),
                  repairs=[Repair(name="Display", price=69), Repair(name="Akku", price=30), Repair(name="Kleinteil", price=45)])

    ip5 = Device(name="iPhone 5",
                 manufacturer=apple,
                 colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_5s').first(),
                 repairs=[Repair(name="Display", price=65), Repair(name="Akku", price=49), Repair(name="Kleinteil", price=49)])

    ip5s = Device(name="iPhone 5s",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_5s').first(),
                  repairs=[Repair(name="Display"), Repair(name="Akku"), Repair(name="Kleinteil"), Repair(name="Wasserschaden")])

    ip5c = Device(name="iPhone 5c",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_5c').first(),
                  repairs=[Repair(name="Display", price=55), Repair(name="Akku", price=49), Repair(name="Kleinteil", price=49)])

    ipse = Device(name="iPhone SE",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_5s').first(),
                  repairs=[Repair(name="Display", price=69), Repair(name="Akku", price=49), Repair(name="Kleinteil", price=69)])

    ip6 = Device(name="iPhone 6",
                 manufacturer=apple,
                 colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_8').first(),
                 repairs=[Repair(name="Display", price=79), Repair(name="Akku", price=49), Repair(name="Kleinteil", price=59)])

    ip6p = Device(name="iPhone 6 Plus",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_8_plus').first(),
                  repairs=[Repair(name="Display", price=79), Repair(name="Akku", price=49), Repair(name="Kleinteil", price=49)])

    ip6s = Device(name="iPhone 6s",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_8').first(),
                  repairs=[Repair(name="Display", price=79), Repair(name="Akku", price=49), Repair(name="Kleinteil", price=79)])

    ip6sp = Device(name="iPhone 6s Plus",
                   manufacturer=apple,
                   colors=[black, white],
                   picture=Picture.query.filter_by(name='iphone_8_plus').first(),
                   repairs=[Repair(name="Display", price=79), Repair(name="Akku", price=49), Repair(name="Kleinteil", price=79)])

    ip7 = Device(name="iPhone 7",
                 manufacturer=apple,
                 colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_8').first(),
                 repairs=[Repair(name="Display Standard", price=85),
                          Repair(name="Display Premium", price=129),
                          Repair(name="Kamera", price=99),
                          Repair(name="Akku", price=49),
                          Repair(name="Kleinteil", price=69),
                          Repair(name="Backcover", price=99)])

    ip7p = Device(name="iPhone 7 Plus",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_8_plus').first(),
                  repairs=[Repair(name="Display Standard", price=95),
                           Repair(name="Display Premium", price=145),
                           Repair(name="Kamera", price=99),
                           Repair(name="Akku", price=49),
                           Repair(name="Kleinteil", price=79),
                           Repair(name="Backcover", price=145)])

    ip8 = Device(name="iPhone 8",
                 manufacturer=apple,
                 colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_x').first(),
                 repairs=[Repair(name="Display Standard", price=95),
                          Repair(name="Display Premium", price=149),
                          Repair(name="Kamera", price=149),
                          Repair(name="Akku", price=49),
                          Repair(name="Kleinteil", price=79),
                          Repair(name="Backcover", price=249)])

    ip8p = Device(name="iPhone 8 Plus",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_x').first(),
                  repairs=[Repair(name="Display Standard", price=105),
                           Repair(name="Display Premium", price=155),
                           Repair(name="Kamera", price=159),
                           Repair(name="Akku", price=49),
                           Repair(name="Kleinteil", price=89),
                           Repair(name="Backcover", price=249)])

    ipx = Device(name="iPhone X",
                 manufacturer=apple,
                 colors=[black, white],
                 picture=Picture.query.filter_by(name='iphone_x').first(),
                 repairs=[Repair(name="Display Standard", price=249),
                          Repair(name="Display Premium", price=329),
                          Repair(name="Kamera", price=129),
                          Repair(name="Backcover", price=289)])

    ipxs = Device(name="iPhone Xs",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_x').first(),
                  repairs=[Repair(name="Display Standard", price=299),
                           Repair(name="Display Premium", price=399),
                           Repair(name="Kamera", price=129),
                           Repair(name="Backcover", price=349)])

    ipxsm = Device(name="iPhone Xs Max",
                   manufacturer=apple,
                   colors=[black, white],
                   picture=Picture.query.filter_by(name='iphone_x').first(),
                   repairs=[Repair(name="Display Standard", price=489),
                            Repair(name="Display Premium", price=559),
                            Repair(name="Kamera", price=129),
                            Repair(name="Backcover", price=369)])

    ipxr = Device(name="iPhone Xr",
                  manufacturer=apple,
                  colors=[black, white],
                  picture=Picture.query.filter_by(name='iphone_x').first(),
                  repairs=[Repair(name="Display Standard", price=239),
                           Repair(name="Display Premium", price=349),
                           Repair(name="Kamera", price=129)])

    db.session.add(ip4)
    db.session.add(ip4s)
    db.session.add(ipse)
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

    db.session.commit()
    if not Device._check_if_paths_are_valid():
        raise ValueError('Some devices have undefined picture paths')
    print('Successfully added sample data')
