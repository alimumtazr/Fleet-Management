from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class UserType(str, Enum):
    RIDER = "rider"
    DRIVER = "driver"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    email: str
    phone: str
    user_type: UserType
    profile_picture: Optional[str] = None
    is_online: bool = False
    current_location: Optional[dict] = None  # {lat: float, lng: float}
    rating: float = 0.0
    total_rides: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class RideStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Ride(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rider_id: str
    driver_id: Optional[str] = None
    pickup_location: dict  # {lat: float, lng: float, address: str}
    dropoff_location: dict  # {lat: float, lng: float, address: str}
    status: RideStatus = RideStatus.PENDING
    estimated_price: float
    actual_price: Optional[float] = None
    distance: float  # in kilometers
    duration: int  # in minutes
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    driver_location_updates: list = []  # List of {lat, lng, timestamp}
    payment_id: Optional[str] = None

    class Config:
        from_attributes = True

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ride_id: str
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: str
    transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ride_id: str
    rated_by: str  # user_id who is giving the rating
    rated_to: str  # user_id who is receiving the rating
    rating: float  # 1-5
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 