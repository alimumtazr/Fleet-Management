from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserType(enum.Enum):
    CUSTOMER = "customer"
    RIDER = "rider"
    DRIVER = "driver"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    rides_as_rider = relationship("Ride", back_populates="rider", foreign_keys="Ride.rider_id")
    rides_as_driver = relationship("Ride", back_populates="driver", foreign_keys="Ride.driver_id")
    payments = relationship("Payment", back_populates="user")
    ratings = relationship("Rating", back_populates="user")

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
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
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
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ride = relationship("Ride", back_populates="payment")
    user = relationship("User", back_populates="payments")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ride = relationship("Ride", back_populates="ratings")
    user = relationship("User", back_populates="ratings") 