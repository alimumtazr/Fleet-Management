from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import datetime
from datetime import timezone  # Import timezone
from passlib.context import CryptContext
from database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserType(enum.Enum):
    CUSTOMER = "customer"
    RIDER = "rider"
    DRIVER = "driver"
    ADMIN = "admin"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class RideStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class NotificationType(enum.Enum):
    RIDE_REQUEST = "ride_request"
    RIDE_ACCEPTED = "ride_accepted"
    DRIVER_ARRIVED = "driver_arrived"
    RIDE_STARTED = "ride_started"
    RIDE_COMPLETED = "ride_completed"
    RIDE_CANCELLED = "ride_cancelled"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    RATING_RECEIVED = "rating_received"
    SYSTEM_MESSAGE = "system_message"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Assuming UUIDs based on main.py
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Renamed from hashed_password for consistency
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)  # URL to profile picture
    user_type = Column(Enum(UserType), nullable=False) # Renamed from role
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc)) # Use timezone.utc
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc), onupdate=lambda: datetime.datetime.now(timezone.utc)) # Use timezone.utc
    
    # Driver specific fields
    is_available = Column(Boolean, default=False)  # Only for drivers
    current_latitude = Column(Float, nullable=True)  # Only for drivers
    current_longitude = Column(Float, nullable=True)  # Only for drivers
    license_number = Column(String, nullable=True)  # Only for drivers
    license_expiry = Column(DateTime, nullable=True)  # Only for drivers
    vehicle_make = Column(String, nullable=True)  # Only for drivers
    vehicle_model = Column(String, nullable=True)  # Only for drivers
    vehicle_year = Column(Integer, nullable=True)  # Only for drivers
    vehicle_color = Column(String, nullable=True)  # Only for drivers
    vehicle_plate = Column(String, nullable=True)  # Only for drivers
    average_rating = Column(Float, default=0.0)  # Average of all ratings received
    total_rides = Column(Integer, default=0)  # Number of rides completed

    # Relationships (adjust foreign keys if needed based on actual schema)
    rides_as_rider = relationship("Ride", back_populates="rider", foreign_keys="Ride.rider_id")
    rides_as_driver = relationship("Ride", back_populates="driver", foreign_keys="Ride.driver_id")
    payments = relationship("Payment", back_populates="user")
    ratings_given = relationship("Rating", back_populates="rater", foreign_keys="Rating.rater_id")
    ratings_received = relationship("Rating", back_populates="ratee", foreign_keys="Rating.ratee_id")

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)
        
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
        
    def update_average_rating(self):
        """Update the user's average rating based on received ratings"""
        total = 0
        count = 0
        for rating in self.ratings_received:
            total += rating.rating
            count += 1
        if count > 0:
            self.average_rating = total / count
        return self.average_rating

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Location information
    pickup_latitude = Column(Float)
    pickup_longitude = Column(Float)
    pickup_address = Column(String, nullable=True)
    destination_latitude = Column(Float)
    destination_longitude = Column(Float)
    destination_address = Column(String, nullable=True)
    
    # Ride status and details
    status = Column(Enum(RideStatus), default=RideStatus.PENDING)
    fare = Column(Float)
    distance = Column(Float, nullable=True)  # in kilometers
    duration = Column(Integer, nullable=True)  # estimated duration in minutes
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    accepted_at = Column(DateTime, nullable=True)
    driver_arrived_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Cancellation
    cancellation_reason = Column(String, nullable=True)
    cancelled_by = Column(String, nullable=True)  # "rider" or "driver"
    
    # Relationships
    rider = relationship("User", back_populates="rides_as_rider", foreign_keys=[rider_id])
    driver = relationship("User", back_populates="rides_as_driver", foreign_keys=[driver_id])
    payment = relationship("Payment", back_populates="ride", uselist=False)
    ratings = relationship("Rating", back_populates="ride")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Payment details
    amount = Column(Float)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String)  # credit_card, debit_card, easypaisa, cash, etc.
    
    # Transaction details
    transaction_id = Column(String, nullable=True)
    payment_provider = Column(String, nullable=True)  # payment processor name if applicable
    card_last_four = Column(String, nullable=True)  # last 4 digits of card if applicable
    
    # Refund details
    refund_amount = Column(Float, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    refund_reason = Column(String, nullable=True)
    
    # Receipt
    receipt_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc), onupdate=lambda: datetime.datetime.now(timezone.utc))

    ride = relationship("Ride", back_populates="payment")
    user = relationship("User", back_populates="payments")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    rater_id = Column(Integer, ForeignKey("users.id"))
    ratee_id = Column(Integer, ForeignKey("users.id"))
    
    # Rating details
    rating = Column(Integer)  # 1-5 stars
    comment = Column(String, nullable=True)
    
    # Additional feedback
    timeliness_rating = Column(Integer, nullable=True)  # 1-5
    cleanliness_rating = Column(Integer, nullable=True)  # 1-5
    communication_rating = Column(Integer, nullable=True)  # 1-5
    driving_rating = Column(Integer, nullable=True)  # 1-5, only for driver ratings
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc), onupdate=lambda: datetime.datetime.now(timezone.utc))

    ride = relationship("Ride", back_populates="ratings")
    rater = relationship("User", back_populates="ratings_given", foreign_keys=[rater_id])
    ratee = relationship("User", back_populates="ratings_received", foreign_keys=[ratee_id])

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(NotificationType))
    title = Column(String)
    message = Column(String)
    related_id = Column(String, nullable=True)  # ID of related object (ride, payment, etc.)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    
    # Relationship
    user = relationship("User", backref="notifications")