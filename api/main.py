from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint
from models import db, User, Post
from config import Config
from datetime import timedelta
import os
 
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)



#Role-based access control decorator
USER_ROLES = {
    'admin': ['create', 'read', 'update', 'delete'],
    'user': ['read']
}

#REGISTER
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Missing username or password'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'User already exists'}), 400

    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'User registered successfully'}), 201

#LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'msg': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 201

# bulk put endpoint
@app.route('/telemetry/bulk', methods=['PUT'])
@jwt_required()
def bulk_update_telemetry():
    claims = get_jwt()
    role = claims.get('role')
    if role != 'admin':
        return jsonify(msg='Insufficient permissions'), 403
    data = request.json
    if not isinstance(data, list):
        return jsonify(msg='Payload must be a list of telemetry records with IDs'), 400
    try:
        for entry in data:
            tid = entry.get('id')
            if not tid:
                return jsonify(msg='Each record must contain an ID'), 400
            telemetry = Telemetry.query.get(tid)
            if not telemetry:
                return jsonify(msg=f'Record with ID {tid} not found'), 404
            # Prevent edits to pre-current quarter records
            if not is_current_quarter(telemetry.timestamp):
                return jsonify(msg=f'Edits to pre-current quarter records are not allowed (ID: {tid})'), 403
            telemetry.buoy_id = entry.get('buoy_id', telemetry.buoy_id)
            telemetry.salinity = entry.get('salinity', telemetry.salinity)
            telemetry.pH = entry.get('pH', telemetry.pH)
            telemetry.pollutants = entry.get('pollutants', telemetry.pollutants)
            telemetry.temperature = entry.get('temperature', telemetry.temperature)
            telemetry.location = entry.get('location', telemetry.location)
        db.session.commit()
        return jsonify(msg='Bulk update successful'), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=str(e)), 400

# Swagger UI setup
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Flask API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 
