from flask import Flask, request
from flask.json import jsonify
from flask_session import Session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from models import *
from config import ApplicationConfig
import psycopg2
import time

app = Flask(__name__)

# An object is called to set up the configuration, it's located in the file "config.py"
app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)

CORS(app, supports_credentials=True)

server_session = Session(app)

def execute_sql_file(filename):
    """
    Execute an SQL script from a file
    """
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="daniel",
        password="7447",
        dbname="buses"
    )
    with open(filename, 'r') as f:
        
        sql = f.read()
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        conn.commit()


def check_db():
    db_ready = False
    while not db_ready:
        try:
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                user="daniel",
                password="7447",
                dbname="buses"
            )
            conn.close()
            print("Database is up!")
            db_ready = True
        except psycopg2.OperationalError:
            print("Waiting for database...")
            time.sleep(1)

    with app.app_context():
        db.create_all()
        
    

db.init_app(app)

@app.route("/register", methods=["POST"])
def register_user():
    email = request.json["email"]
    name = request.json["name"]
    password = request.json["password"]
    role = request.json["role"]

    user_exists = Users.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "Usuario ya existe"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = Users(email=email, name=name, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Usuario registrado"
    }), 200


@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = Users.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "No autorizado"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):

        return jsonify({"error": "No autorizado"}), 401
    
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }), 200


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


@app.route("/update-bus", methods=["PUT"])
def update_bus():
    bus_id = request.json["bus_id"]
    bus_name = request.json["bus_name"]

    bus = Buses.query.get(bus_id)

    if not bus:
        return jsonify({"error": "Bus no encontrado"}), 404
    
    bus.bus_name = bus_name
    db.session.commit()
    return  jsonify({"message": "Actualizado"}), 200


@app.route("/delete-bus", methods=["DELETE"])
def delete_bus():
    print(request.json)
    bus_id = request.json["bus_id"]

    bus = Buses.query.get(bus_id)

    if bus is None:
        return jsonify({"error": "No existe el bus"}), 404
    
    try:
        db.session.delete(bus)
        db.session.commit()
    except:
        db.session.rollback()
        return  jsonify({"error": "Error al borrar el bus"}), 500
    
    return jsonify({"message": "Se ha borrado el bus"}), 200


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


@app.route("/delete-hour", methods=["DELETE"])
def delete_hour():
    hour_id = request.json["hour_id"]

    hour = Hours.query.get(hour_id)

    if hour is None:
        return jsonify({"error": "No existe la hora"}), 404
    
    try:
        db.session.delete(hour)
        db.session.commit()
    except:
        db.session.rollback()
        return  jsonify({"error": "Error al borrar la hora"}), 500
    
    return jsonify({"message": "Se ha borrado la hora"}), 200


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
    print(request.json)
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


@app.route("/update-location", methods=["PUT"])
def update_location():
    location_id = request.json["location_id"]
    location_name = request.json["location_name"]
    latitude = request.json["latitude"]
    longitude = request.json["longitude"]

    location = Location.query.get(location_id)

    if not location:
        return jsonify({"error": "Bus no encontrado"}), 404
    
    location.location_name = location_name
    location.latitude = latitude
    location.longitude = longitude

    db.session.commit()
    return  jsonify({"message": "Actualizado"}), 200


@app.route("/delete-location", methods=["DELETE"])
def delete_location():
    location_id = request.json["location_id"]

    location = Location.query.get(location_id)

    if location is None:
        return jsonify({"error": "No existe la ubicación"}), 404
    
    try:
        db.session.delete(location)
        db.session.commit()
    except:
        db.session.rollback()
        return  jsonify({"error": "Error al borrar la ubicación"}), 500
    
    return jsonify({"message": "Se ha borrado la ubicación"}), 200


@app.route("/buses-hours", methods=["GET"])
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


@app.route("/buses-hours/<int:bus_id>", methods=["GET"])
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


@app.route("/create-bus-hour", methods=["POST"])
def create_bus_hour():
    bus_id = request.json["bus_id"]
    hour_id = request.json["hour_id"]
    
    new_bus_hour = BusesHours(bus_id=bus_id, hour_id=hour_id)
    db.session.add(new_bus_hour)
    db.session.commit()
    
    return jsonify({
        "message": "Hora añadida exitosamente al bus"
    })


@app.route("/delete-bus-hour", methods=["DELETE"])
def delete_bus_hour():
    bus_id = request.json["bus_id"]
    hour_id = request.json["hour_id"]

    bus_hour = BusesHours.query.filter_by(bus_id=bus_id, hour_id=hour_id).first()
    
    if bus_hour is None:
        return jsonify({"error": "No existe la hora en el bus seleccionado"}), 404
    
    try:
        db.session.delete(bus_hour)
        db.session.commit()
    except:
        db.session.rollback()
        return  jsonify({"error": "Error al borrar la hora en el bus seleccionado"}), 500
    
    return jsonify({"message": "Se ha borrado la hora en el bus seleccionado"}), 200


@app.route("/info-buses", methods=["GET"])
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
    check_db()
    app.run(host='0.0.0.0', port=8000)