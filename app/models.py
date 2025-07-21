from app.program import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

'''
changed ride type relation ship to be a one to many from a many to many

# Association table for many-to-many relationship between RideType and Manufacturer
RideTypeManufacturer = db.Table('RideType_Manufacturer',
    db.Column('ride_type_id', db.Integer, db.ForeignKey('ride_type.id')),
    db.Column('manufacturer_id', db.Integer, db.ForeignKey('manufacturer.id'))
)
'''
# Association table for ride elements and layouts
RideElementsLayout = db.Table('rideelements_layout',
    db.Column('ride_elements_id', db.Integer, db.ForeignKey('ride_elements.id')),
    db.Column('layout_id', db.Integer, db.ForeignKey('layout.id')),
    db.Column('count', db.Integer)
)

# Association table for many-to-many relationship between Park and Ride
ParkRide = db.Table('park_ride',
    db.Column('park_id', db.Integer, db.ForeignKey('park.id')),
    db.Column('ride_id', db.Integer, db.ForeignKey('ride.id')),
    db.Column('photo', db.Text)
)

class Manufacturer(db.Model):
    __tablename__ = 'manufacturer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    photo = db.Column(db.Text)

    #ride_types = db.relationship('RideType', secondary=RideTypeManufacturer, back_populates='manufacturers')
    ride_types = db.relationship('RideType', back_populates='manufacturer')


class RideType(db.Model):
    __tablename__ = 'ride_type'
    id = db.Column(db.Integer, primary_key=True)
    ride = db.Column(db.Text)
    description = db.Column(db.Text)
    track_photo = db.Column(db.Text)
    train_photo = db.Column(db.Text)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'))
    
    manufacturer = db.relationship('Manufacturer', back_populates='ride_types')
    rides = db.relationship('Ride', backref='ride_type')


class RideElement(db.Model):
    __tablename__ = 'ride_elements'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    inverted = db.Column(db.Integer)
    photo = db.Column(db.Text)


class LaunchType(db.Model):
    __tablename__ = 'launch_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    lift_launch = db.Column(db.Integer)  # 0 = Lift, 1 = Launch

    rides = db.relationship('Ride', backref='launch_type')


class Layout(db.Model):
    __tablename__ = 'layout'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    photo = db.Column(db.Text)

    rides = db.relationship('Ride', backref='layout')


class Restriction(db.Model):
    __tablename__ = 'restrictions'
    id = db.Column(db.Integer, primary_key=True)
    min = db.Column(db.Integer)
    max = db.Column(db.Integer)
    reason = db.Column(db.Text)

    rides = db.relationship('Ride', backref='restriction')


class Theme(db.Model):
    __tablename__ = 'theme'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)

    rides = db.relationship('Ride', backref='theme')


class Constructor(db.Model):
    __tablename__ = 'constructor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    location = db.Column(db.Integer)
    photo = db.Column(db.Text)

    rides = db.relationship('Ride', backref='constructor')


class Ride(db.Model):
    __tablename__ = 'ride'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    ride_type_id = db.Column(db.Integer, db.ForeignKey('ride_type.id'))
    layout_id = db.Column(db.Integer, db.ForeignKey('layout.id'))
    theme_id = db.Column(db.Integer, db.ForeignKey('theme.id'))
    launch_type_id = db.Column(db.Integer, db.ForeignKey('launch_type.id'))
    thrill_level = db.Column(db.Text)
    restriction_id = db.Column(db.Integer, db.ForeignKey('restrictions.id'))
    constructor_id = db.Column(db.Integer, db.ForeignKey('constructor.id'))
    photo = db.Column(db.Text)
    height = db.Column(db.Integer)

    parks = db.relationship('Park', secondary=ParkRide, back_populates='rides')
    review = db.relationship('Review', backref='ride', lazy='dynamic')


class Park(db.Model):
    __tablename__ = 'park'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    location = db.Column(db.Integer)
    photo = db.Column(db.Text)

    rides = db.relationship('Ride', secondary=ParkRide, back_populates='parks')
    review = db.relationship('Review', backref='park', lazy='dynamic')


# login tables for flask session

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Text, default=True)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='reviews')

    # Foreign keys to Ride or Park. Null if it's a site review.
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=True)
    park_id = db.Column(db.Integer, db.ForeignKey('park.id'), nullable=True)

    ride = db.relationship('Ride', backref='reviews')
    park = db.relationship('Park', backref='reviews')

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id}>'
