from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'driver', 'customer'
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional fields for drivers
    license_number = db.Column(db.String(50))
    vehicle_info = db.Column(db.JSON)
    current_location = db.Column(db.JSON)
    is_available = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    total_rides = db.Column(db.Integer, default=0)

    def __init__(self, email, password, role, first_name, last_name, phone_number, **kwargs):
        self.email = email.lower()
        self.set_password(password)
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        
        # Set additional driver fields if provided
        if role == 'driver':
            self.license_number = kwargs.get('license_number')
            self.vehicle_info = kwargs.get('vehicle_info', {})
            self.current_location = kwargs.get('current_location', {})
            self.is_available = kwargs.get('is_available', True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if self.role == 'driver':
            data.update({
                'license_number': self.license_number,
                'vehicle_info': self.vehicle_info,
                'current_location': self.current_location,
                'is_available': self.is_available,
                'rating': self.rating,
                'total_rides': self.total_rides
            })

        return data

    @staticmethod
    def create_admin():
        """Create default admin user if not exists"""
        admin = User.query.filter_by(email='admin@fms.com').first()
        if not admin:
            admin = User(
                email='admin@fms.com',
                password='admin123',  # This should be changed after first login
                role='admin',
                first_name='Admin',
                last_name='User',
                phone_number='0000000000'
            )
            db.session.add(admin)
            db.session.commit()
            return admin
        return None 