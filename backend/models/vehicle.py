from app import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Float)
    fuel_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default='available')
    last_maintenance = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Vehicle {self.vehicle_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_number': self.vehicle_number,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'capacity': self.capacity,
            'fuel_type': self.fuel_type,
            'status': self.status,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 