from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default="user")  # 'admin', 'researcher', 'consumer', 'user', 'buoy'

    # If a user can be a buoy device, this links its telemetry
    telemetry = db.relationship("Telemetry", backref="buoy", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class Telemetry(db.Model):
    __tablename__ = "telemetry"

    id = db.Column(db.Integer, primary_key=True)
    buoy_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    # Use Float for numeric metrics. Column name 'ph' while Python attribute is 'pH' for compatibility with existing code.
    salinity = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    pH = db.Column("ph", db.Float, nullable=False)

    # Optional fields
    pollutants = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=True)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Telemetry {self.id} - Buoy {self.buoy_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "buoy_id": self.buoy_id,
            "salinity": self.salinity,
            "temperature": self.temperature,
            "pH": self.pH,
            "pollutants": self.pollutants,
            "location": self.location,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
