from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str
    is_driver: bool = False

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class RideBase(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float

class RideCreate(RideBase):
    pass

class Ride(RideBase):
    id: int
    rider_id: int
    driver_id: Optional[int]
    status: str
    fare: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    amount: float
    payment_method: str

class PaymentCreate(PaymentBase):
    ride_id: int

class Payment(PaymentBase):
    id: int
    ride_id: int
    user_id: int
    status: str
    transaction_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class RatingBase(BaseModel):
    rating: int
    comment: Optional[str]

class RatingCreate(RatingBase):
    ride_id: int

class Rating(RatingBase):
    id: int
    ride_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float

class RideStatusUpdate(BaseModel):
    status: str
    driver_id: Optional[int] = None 