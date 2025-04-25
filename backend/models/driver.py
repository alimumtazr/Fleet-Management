from app import db
from datetime import datetime

class Driver(db.Model):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_expiry = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True)
    status = db.Column(db.String(50), default='active')
    date_of_birth = db.Column(db.Date)
    hire_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Driver {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'license_number': self.license_number,
            'license_expiry': self.license_expiry.isoformat(),
            'phone_number': self.phone_number,
            'email': self.email,
            'status': self.status,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 