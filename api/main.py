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


@app.route('/api/data', methods=['GET'])
def get_data():
    response = {
        'message': 'Hello, World!'
    }
    return jsonify(response)

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.json
    response = {
        'message': 'Data received!',
        'data': data
    }
    return jsonify(response)



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