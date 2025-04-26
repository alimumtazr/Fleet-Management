from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import User, Ride, Payment, Rating, UserType, RideStatus
from realtime_service import manager
import json
from datetime import datetime
import uuid
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:cassinispacecraft@localhost:5432/fms_data")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class DBUser(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    user_type = Column(SQLEnum(UserType))
    profile_picture = Column(String, nullable=True)
    is_online = Column(Boolean, default=False)
    current_location = Column(String, nullable=True)  # Store as JSON string
    rating = Column(Float, default=0.0)
    total_rides = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DBRide(Base):
    __tablename__ = "rides"
    id = Column(String, primary_key=True)
    rider_id = Column(String, ForeignKey("users.id"))
    driver_id = Column(String, ForeignKey("users.id"), nullable=True)
    pickup_location = Column(String)  # Store as JSON string
    dropoff_location = Column(String)  # Store as JSON string
    status = Column(SQLEnum(RideStatus), default=RideStatus.PENDING)
    estimated_price = Column(Float)
    actual_price = Column(Float, nullable=True)
    distance = Column(Float)
    duration = Column(Integer)
    requested_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String, nullable=True)
    driver_location_updates = Column(String, nullable=True)  # Store as JSON string
    payment_id = Column(String, ForeignKey("payments.id"), nullable=True)

class DBPayment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True)
    ride_id = Column(String, ForeignKey("rides.id"))
    amount = Column(Float)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String)
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class DBRating(Base):
    __tablename__ = "ratings"
    id = Column(String, primary_key=True)
    ride_id = Column(String, ForeignKey("rides.id"))
    rated_by = Column(String, ForeignKey("users.id"))
    rated_to = Column(String, ForeignKey("users.id"))
    rating = Column(Float)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ride-Hailing API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=User)
async def create_user(user: User, db: Session = Depends(get_db)):
    db_user = DBUser(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_orm(db_user)

@app.post("/rides/", response_model=Ride)
async def create_ride(ride: Ride, db: Session = Depends(get_db)):
    db_ride = DBRide(**ride.dict())
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    return ride

@app.get("/rides/{ride_id}", response_model=Ride)
async def get_ride(ride_id: str, db: Session = Depends(get_db)):
    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
    if not db_ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return Ride.from_orm(db_ride)

@app.put("/rides/{ride_id}/accept")
async def accept_ride(ride_id: str, driver_id: str, db: Session = Depends(get_db)):
    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
    if not db_ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    db_driver = db.query(DBUser).filter(DBUser.id == driver_id).first()
    if not db_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db_ride.status = RideStatus.ACCEPTED
    db_ride.driver_id = driver_id
    db_ride.accepted_at = datetime.utcnow()
    db.commit()
    
    await manager.broadcast_ride_update(ride_id, {
        "type": "ride_accepted",
        "data": {
            "ride_id": ride_id,
            "driver_id": driver_id,
            "driver_info": User.from_orm(db_driver).dict()
        }
    })
    
    return {"message": "Ride accepted successfully"}

@app.put("/rides/{ride_id}/start")
async def start_ride(ride_id: str, db: Session = Depends(get_db)):
    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
    if not db_ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    db_ride.status = RideStatus.IN_PROGRESS
    db_ride.started_at = datetime.utcnow()
    db.commit()
    
    await manager.broadcast_ride_update(ride_id, {
        "type": "ride_started",
        "data": {
            "ride_id": ride_id,
            "started_at": db_ride.started_at.isoformat()
        }
    })
    
    return {"message": "Ride started successfully"}

@app.put("/rides/{ride_id}/complete")
async def complete_ride(ride_id: str, db: Session = Depends(get_db)):
    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
    if not db_ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    db_ride.status = RideStatus.COMPLETED
    db_ride.completed_at = datetime.utcnow()
    db.commit()
    
    await manager.broadcast_ride_update(ride_id, {
        "type": "ride_completed",
        "data": {
            "ride_id": ride_id,
            "completed_at": db_ride.completed_at.isoformat()
        }
    })
    
    return {"message": "Ride completed successfully"}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "location_update":
                await manager.update_driver_location(user_id, data["location"])
            elif data["type"] == "subscribe_ride":
                await manager.subscribe_to_ride_updates(data["ride_id"], websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.get("/nearby-drivers")
async def get_nearby_drivers(lat: float, lng: float, radius_km: float = 5.0):
    location = {"lat": lat, "lng": lng}
    nearby_drivers = manager._get_nearby_drivers(location, radius_km)
    return {"drivers": nearby_drivers}

@app.post("/payments/", response_model=Payment)
async def create_payment(payment: Payment, db: Session = Depends(get_db)):
    db_payment = DBPayment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return payment

@app.post("/ratings/", response_model=Rating)
async def create_rating(rating: Rating, db: Session = Depends(get_db)):
    db_rating = DBRating(**rating.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return rating 