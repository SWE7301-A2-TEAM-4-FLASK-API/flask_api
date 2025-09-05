from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

 
class Telemetry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buoy_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    salinity = db.Column(db.Text, nullable=False)
    temperature = db.Column(db.Text, nullable=False)
    pH = db.Column(db.Text, nullable=False)
    pollution_level = db.Column(db.Text, nullable=False)
    dissolved_oxygen = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def _repr_(self):
        return f'<Telemetry {self.id} - Buoy {self.buoy_id}>'