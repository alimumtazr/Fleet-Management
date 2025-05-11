import os
import sys
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import models and database connection
from database import engine, SessionLocal, Base
from models import UserType, RideStatus, PaymentStatus, NotificationType, User, Ride, Payment, Rating, Notification

def init_db():
    """
    Initialize the database by creating all tables and setting up initial data.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter_by(email="admin@example.com").first()
        if not admin_user:
            # Create admin user
            from auth import get_password_hash
            
            admin_user = User(
                id="admin-001",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                user_type=UserType.ADMIN,
                phone_number="123456789",
                is_active=True
            )
            db.add(admin_user)
            print("Created admin user")
            
            # Create test driver
            driver_user = User(
                id="driver-001",
                email="driver@example.com",
                password_hash=get_password_hash("driver123"),
                first_name="Test",
                last_name="Driver",
                user_type=UserType.DRIVER,
                phone_number="987654321",
                is_active=True,
                license_number="DL-12345",
                vehicle_make="Toyota",
                vehicle_model="Corolla",
                vehicle_year=2020,
                vehicle_color="Blue",
                vehicle_plate="ABC-123",
                is_available=True,
                average_rating=4.8
            )
            db.add(driver_user)
            print("Created test driver")
            
            # Create test customer
            customer_user = User(
                id="customer-001",
                email="customer@example.com",
                password_hash=get_password_hash("customer123"),
                first_name="Test",
                last_name="Customer",
                user_type=UserType.CUSTOMER,
                phone_number="456789123",
                is_active=True
            )
            db.add(customer_user)
            print("Created test customer")
            
            db.commit()
        else:
            print("Admin user already exists")
        
        # Print database statistics
        print("\nDatabase Statistics:")
        print(f"Users: {db.query(User).count()}")
        print(f"Rides: {db.query(Ride).count()}")
        print(f"Payments: {db.query(Payment).count()}")
        print(f"Ratings: {db.query(Rating).count()}")
        print(f"Notifications: {db.query(Notification).count()}")
        
        print("\nDatabase initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 