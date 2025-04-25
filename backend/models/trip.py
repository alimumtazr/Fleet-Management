from app import db
from datetime import datetime

class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    start_location = db.Column(db.String(200), nullable=False)
    end_location = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='scheduled')
    distance = db.Column(db.Float)
    fuel_consumption = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = db.relationship('Vehicle', backref=db.backref('trips', lazy=True))
    driver = db.relationship('Driver', backref=db.backref('trips', lazy=True))

    def __repr__(self):
        return f'<Trip {self.id}: {self.start_location} to {self.end_location}>'

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'driver_id': self.driver_id,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'distance': self.distance,
            'fuel_consumption': self.fuel_consumption,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 