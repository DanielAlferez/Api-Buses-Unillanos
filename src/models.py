from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from sqlalchemy import Sequence

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(100))
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)

class Buses(db.Model):
    __tablename__ = "buses"
    bus_id = db.Column(db.Integer, Sequence('bus_id_seq'), primary_key=True, unique=True)
    bus_name = db.Column(db.String(100), unique=True, nullable=False)

class Location(db.Model):
    __tablename__ = "locations"
    location_id = db.Column(db.Integer, Sequence('location_id_seq'), primary_key=True, unique=True)
    location_name = db.Column(db.String(100), unique=True, nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longitude = db.Column(db.String(50), nullable=False)

class Hours(db.Model):
    __tablename__ = "hours"
    hour_id = db.Column(db.Integer, Sequence('hour_id_seq'), primary_key=True, unique=True)
    hour_name = db.Column(db.String(100), unique=True, nullable=False)

class BusesHours(db.Model):
    __tablename__ = "buses_hours"
    bus_id = db.Column(db.Integer, db.ForeignKey('buses'), primary_key=True)
    hour_id = db.Column(db.Integer, db.ForeignKey('hours'), primary_key=True)

class BusesLocations(db.Model):
    __tablename__ = "buses_locations"
    bus_id = db.Column(db.Integer, db.ForeignKey('buses'), primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations'), primary_key=True)