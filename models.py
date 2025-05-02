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

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Assuming UUIDs based on main.py
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Renamed from hashed_password for consistency
    first_name = Column(String)
    last_name = Column(String)
    user_type = Column(Enum(UserType), nullable=False) # Renamed from role
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc)) # Use timezone.utc
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc), onupdate=lambda: datetime.datetime.now(timezone.utc)) # Use timezone.utc

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

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    pickup_latitude = Column(Float)
    pickup_longitude = Column(Float)
    destination_latitude = Column(Float)
    destination_longitude = Column(Float)
    status = Column(String)  # requested, accepted, in_progress, completed, cancelled
    fare = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc)) # Use timezone.utc
    completed_at = Column(DateTime, nullable=True)

    rider = relationship("User", back_populates="rides_as_rider", foreign_keys=[rider_id])
    driver = relationship("User", back_populates="rides_as_driver", foreign_keys=[driver_id])
    payment = relationship("Payment", back_populates="ride", uselist=False)
    ratings = relationship("Rating", back_populates="ride")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    status = Column(String)  # pending, completed, failed
    payment_method = Column(String)
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc)) # Use timezone.utc

    ride = relationship("Ride", back_populates="payment")
    user = relationship("User", back_populates="payments")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    rater_id = Column(Integer, ForeignKey("users.id"))  # Changed from user_id to rater_id
    ratee_id = Column(Integer, ForeignKey("users.id"))  # Added ratee_id column
    rating = Column(Integer)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))

    ride = relationship("Ride", back_populates="ratings")
    rater = relationship("User", back_populates="ratings_given", foreign_keys=[rater_id])
    ratee = relationship("User", back_populates="ratings_received", foreign_keys=[ratee_id])