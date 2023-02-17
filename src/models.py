from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class Users(db.Model):
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(100))
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50))

class Buses(db.Model):
    bus_id = db.Column(db.Integer, primary_key=True)
    bus_name = db.Column(db.String(100), unique=True, nullable=False)

class Location(db.Model):
    location_id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), unique=True, nullable=False)
    latitude = db.Column(db.String(50), nullable=False)
    longitude = db.Column(db.String(50), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.bus_id', ondelete="CASCADE"), nullable=False)
    bus = db.relationship('Buses', uselist=True)

class Hours(db.Model):
    hour_id = db.Column(db.Integer, primary_key=True)
    hour_name = db.Column(db.String(10), unique=True, nullable=False)
    
class BusesHours(db.Model):
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.bus_id', ondelete="CASCADE"), nullable=False, primary_key=True)
    bus = db.relationship('Buses', uselist=True)
    hour_id = db.Column(db.Integer, db.ForeignKey('hours.hour_id', ondelete="CASCADE"), nullable=False, primary_key=True)
    hour = db.relationship('Hours', uselist=True)