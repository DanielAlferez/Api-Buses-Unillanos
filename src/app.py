from flask import Flask, request, session
from flask.json import jsonify
from flask_session import Session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from models import *
from config import ApplicationConfig

app = Flask(__name__)

# An object is called to set up the configuration, it's located in the file "config.py"
app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/@me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "No autorizado"}), 409
    
    user = User.query.filter_by(id=user_id).first()

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
    })


@app.route("/register", methods=["POST"])
def register_user():
    email = request.json["email"]
    name = request.json["name"]
    password = request.json["password"]

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "Usuario ya existe"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password)

    new_user = User(email=email, name=name, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
    })


@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "No autorizado"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "No autorizado"}), 401
    
    session["user_id"] = user.id
    
    return jsonify({
        "id": user.id,
        "email": user.email,
    }) 


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"


@app.route("/buses", methods=["GET"])
def get_buses():
    buses = Buses.query.all()
    serialized_buses = []
    for bus in buses:
        serialized_bus = {
            'bus_id': bus.bus_id,
            'bus_name': bus.bus_name,
        }
        serialized_buses.append(serialized_bus)

    return jsonify(serialized_buses)


@app.route("/buses/<int:bus_id>", methods=["GET"])
def get_bus(bus_id):

    bus = Buses.query.filter_by(bus_id=bus_id).first()

    return jsonify({
        'bus_id': bus.bus_id,
        'bus_name': bus.bus_name,
    })


@app.route("/create-bus", methods=["POST"])
def create_bus():
    bus_name = request.json["bus_name"]
    bus_exists = Buses.query.filter_by(bus_name=bus_name).first() is not None

    if bus_exists:
        return jsonify({"error": "Bus ya existe"}), 409
    
    new_bus = Buses(bus_name=bus_name)
    db.session.add(new_bus)
    db.session.commit()
    
    return jsonify({
        "message": "Bus añadido exitosamente"
    })

@app.route("/hours", methods=["GET"])
def get_hours():
    hours = Hours.query.all()
    serialized_hours = []
    for hour in hours:
        serialized_hour = {
            'hours_id': hour.hour_id,
            'hours_name': hour.hour_name,
        }
        serialized_hours.append(serialized_hour)

    return jsonify(serialized_hours)


@app.route("/hours/<int:hour_id>", methods=["GET"])
def get_hour(hour_id):

    hour = Hours.query.filter_by(hour_id=hour_id).first()

    return jsonify({
        'hour_id': hour.hour_id,
        'hour_name': hour.hour_name,
    })


@app.route("/create-hour", methods=["POST"])
def create_hour():
    hour_name = request.json["hour_name"]
    hour_exists = Hours.query.filter_by(hour_name=hour_name).first() is not None

    if hour_exists:
        return jsonify({"error": "Hora ya existe"}), 409
    
    new_hour = Hours(hour_name=hour_name)
    db.session.add(new_hour)
    db.session.commit()
    
    return jsonify({
        "message": "Hora añadida exitosamente"
    })


@app.route("/locations", methods=["GET"])
def get_locations():
    locations = Location.query.all()
    serialized_locations = []
    for location in locations:
        serialized_location = {
            'locations_id': location.location_id,
            'locations_name': location.location_name,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'bus_id': location.bus_id,
        }
        serialized_locations.append(serialized_location)

    return jsonify(serialized_locations)


@app.route("/locations/<int:location_id>", methods=["GET"])
def get_location(location_id):

    location = Location.query.filter_by(location_id=location_id).first()

    return jsonify({
        'location_id': location.location_id,
        'location_name': location.location_name,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'bus_id': location.bus_id,
    })


@app.route("/create-location", methods=["POST"])
def create_location():
    location_name = request.json["location_name"]
    latitude = request.json["latitude"]
    longitude = request.json["longitude"]
    bus_id = request.json["bus_id"]

    location_exists = Location.query.filter_by(location_name=location_name).first() is not None

    if location_exists:
        return jsonify({"error": "Ubicación ya existe"}), 409
    
    new_location = Location(location_name=location_name, latitude=latitude, longitude=longitude, bus_id=bus_id)
    db.session.add(new_location)
    db.session.commit()
    
    return jsonify({
        "message": "Ubicación añadida exitosamente"
    })


@app.route("/buses_hours", methods=["GET"])
def get_buses_hours():
    buses_hours = BusesHours.query.all()
    serialized_buses_hours = []
    for bus_hour in buses_hours:
        serialized_bus_hour = {
            'bus_id': bus_hour.bus_id,
            'hour_id': bus_hour.hour_id
        }
        serialized_buses_hours.append(serialized_bus_hour)

    return jsonify(serialized_buses_hours)


@app.route("/buses_hours/<int:bus_id>", methods=["GET"])
def get_bus_hour(bus_id):

    bus_hours = BusesHours.query.filter_by(bus_id=bus_id).all()

    serialized_buses_hours = []
    for bus_hour in bus_hours:
        serialized_bus_hour = {
            'hour_id': bus_hour.hour_id,
        }
        serialized_buses_hours.append(serialized_bus_hour)

    return jsonify({
        'bus_id': bus_hour.bus_id,
        'hours': serialized_buses_hours
    })


@app.route("/create_bus_hour", methods=["POST"])
def create_bus_hour():
    bus_id = request.json["bus_id"]
    hour_id = request.json["hour_id"]
    
    new_bus_hour = BusesHours(bus_id=bus_id, hour_id=hour_id)
    db.session.add(new_bus_hour)
    db.session.commit()
    
    return jsonify({
        "message": "Hora añadida exitosamente al bus"
    })


@app.route("/info_buses", methods=["GET"])
def get_info_buses():

    buses = Buses.query.all()

    serialized_buses = []
    for bus in buses:
        bus_hours = BusesHours.query.filter_by(bus_id=bus.bus_id).all()
        serialized_buses_hours = []
        for bus_hour in bus_hours:
            hours = Hours.query.filter_by(hour_id=bus_hour.hour_id).first()
            serialized_bus_hour = {
                'hour_id': bus_hour.hour_id,
                'hour_name': hours.hour_name
            }
            serialized_buses_hours.append(serialized_bus_hour)

        locations = Location.query.filter_by(bus_id=bus.bus_id).all()
        serialized_locations = []
        for location in locations:
            serialized_location = {
                'location_id': location.location_id,
                'location_name': location.location_name,
                'latitude': location.latitude,
                'longitude': location.longitude,
            }
            serialized_locations.append(serialized_location)

        serialized_bus = {
            'bus_id': bus.bus_id,
            'bus_name': bus.bus_name,
            'hours': serialized_buses_hours,
            'locations': serialized_locations
        }
        serialized_buses.append(serialized_bus)

    return serialized_buses

if __name__ == "__main__":
    app.run(debug=True)