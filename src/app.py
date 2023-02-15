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

if __name__ == "__main__":
    app.run(debug=True)