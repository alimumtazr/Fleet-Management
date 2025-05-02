from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import UserType, RideStatus, User as DBUser, Ride as DBRide, Payment as DBPayment, Rating as DBRating
from realtime_service import manager
import json
from datetime import timedelta
import datetime
import uuid
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from database import get_db, engine
from auth import (
    get_current_active_user,
    get_current_user,
    create_access_token,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# Add this line to create the OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

load_dotenv()

# Database setup is now handled in database.py
# We'll use the engine and SessionLocal from there
from database import engine, SessionLocal, Base

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

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper status codes and details."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions to prevent server crashes."""
    # Log the error for server-side debugging
    import traceback
    error_details = traceback.format_exc()
    print(f"Unhandled exception: {str(exc)}\n{error_details}")

    # Return a user-friendly error response
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "An unexpected error occurred. Please try again later.",
            "path": request.url.path
        }
    )

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    user_type: str  # Make sure this matches what frontend sends

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RideCreate(BaseModel):
    pickup_location: str
    dropoff_location: str
    pickup_lat: float
    pickup_lng: float
    dropoff_lat: float
    dropoff_lng: float

@app.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        db_user = db.query(DBUser).filter(DBUser.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user with UUID
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user.password)

        # Fix: Make sure all required fields are provided and match the DB model
        db_user = DBUser(
            id=user_id,
            email=user.email,
            password_hash=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            user_type=UserType(user.user_type),
            is_active=True
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        db.rollback()  # Rollback transaction on error
        print(f"Registration error: {str(e)}")  # Log the error
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# Add API endpoint for frontend compatibility
@app.post("/api/auth/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists - return a clean 400 error
        db_user = db.query(DBUser).filter(DBUser.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,  # Use 409 for resource conflict
                detail="Email already registered"
            )

        # Create new user with UUID
        user_id = str(uuid.uuid4())
        
        # Ensure password is hashed properly with improved error handling
        try:
            hashed_password = get_password_hash(user.password)
            print(f"Password hashed successfully, length: {len(hashed_password)}")
        except Exception as hash_error:
            print(f"Password hashing error: {str(hash_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing password"
            )

        # Fix: Make sure all required fields are provided and match the DB model
        db_user = DBUser(
            id=user_id,
            email=user.email,
            password_hash=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            user_type=UserType(user.user_type),
            is_active=True
        )

        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            print(f"User registered successfully: {user.email}")
        except Exception as db_error:
            db.rollback()
            print(f"Database error during registration: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during registration"
            )

        # Create access token
        try:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user_id}, expires_delta=access_token_expires
            )
            print(f"Token generated with expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        except Exception as token_error:
            print(f"Token generation error: {str(token_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating authentication token"
            )

        return {
            "status": "success",
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user.user_type
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions so they're handled properly
        raise
    except Exception as e:
        db.rollback()  # Rollback transaction on error
        print(f"Unexpected registration error: {str(e)}")  # Log the error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an unexpected error"
        )

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Add API endpoint for frontend compatibility
@app.post("/api/auth/login")
async def login_api(user_login: UserLogin, db: Session = Depends(get_db)):
    try:
        # Check if user exists and password is correct
        db_user = db.query(DBUser).filter(DBUser.email == user_login.email).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Add extra debugging
        print(f"Attempting to verify password for user: {db_user.email}")
        print(f"Password hash in DB: {db_user.password_hash[:20]}...")

        if not verify_password(user_login.password, db_user.password_hash):
            print("Password verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate access token
        try:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(db_user.id)}, expires_delta=access_token_expires
            )
            print(f"Token generated with expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        except Exception as token_error:
            print(f"Token generation error during login: {str(token_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating authentication token"
            )

        return {
            "status": "success",
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "email": db_user.email,
                "first_name": db_user.first_name,
                "last_name": db_user.last_name,
                "user_type": str(db_user.user_type.value)
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions so they're handled properly
        raise
    except Exception as e:
        print(f"Unexpected login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to an unexpected error"
        )

@app.get("/users/me", response_model=None)
async def read_users_me(current_user: DBUser = Depends(get_current_active_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "user_type": current_user.user_type,
        "is_active": current_user.is_active
    }

# Add API endpoint for frontend compatibility
@app.get("/api/auth/me")
async def get_current_user_api(current_user: DBUser = Depends(get_current_user)):
    """
    Get the current user's information.
    This endpoint is used by the frontend to check if the user is logged in.
    """
    try:
        # Return consistent user information format
        return {
            "status": "success", 
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "user_type": str(current_user.user_type.value),
                "is_active": current_user.is_active
            }
        }
    except Exception as e:
        print(f"Error in /api/auth/me endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )

# Add this route to redirect users based on their type
@app.get("/api/auth/redirect")
async def redirect_based_on_user_type(request: Request, db: Session = Depends(get_db)):
    """
    Redirect users to the appropriate dashboard based on their user type.
    """
    try:
        # Get the current user using our updated function
        current_user = await get_current_user(request, db)
        
        # Determine the redirect path based on user type
        user_type = current_user.user_type.value if current_user.user_type else None
        redirect_path = f"/{user_type.lower()}-dashboard" if user_type else "/login"
        
        return {
            "status": "success",
            "redirect": redirect_path,
            "user_type": user_type
        }
    except HTTPException:
        # If authentication fails, redirect to login
        return {
            "status": "error",
            "redirect": "/login",
            "message": "Authentication required"
        }
    except Exception as e:
        print(f"Error in redirect endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error determining user redirect"
        )

@app.post("/rides", response_model=dict)
async def create_ride(
    ride: RideCreate,
    current_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_ride = DBRide(
        rider_id=current_user.id,
        pickup_location=ride.pickup_location,
        dropoff_location=ride.dropoff_location,
        pickup_lat=ride.pickup_lat,
        pickup_lng=ride.pickup_lng,
        dropoff_lat=ride.dropoff_lat,
        dropoff_lng=ride.dropoff_lng
    )
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    return db_ride.__dict__

@app.get("/rides", response_model=List[dict])
async def get_rides(
    current_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    rides = db.query(DBRide).filter(DBRide.rider_id == current_user.id).all()
    return [ride.__dict__ for ride in rides]

@app.post("/users/", response_model=dict)
async def create_user(user: dict, db: Session = Depends(get_db)):
    db_user = DBUser(**user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user

@app.get("/users/{user_id}", response_model=dict)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": db_user.id,
        "email": db_user.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "user_type": str(db_user.user_type.value),
        "is_active": db_user.is_active
    }

@app.post("/rides/", response_model=dict)
async def create_ride(ride: dict, db: Session = Depends(get_db)):
    db_ride = DBRide(**ride)
    db.add(db_ride)
    db.commit()
    db.refresh(db_ride)
    return ride

@app.get("/rides/{ride_id}", response_model=dict)
async def get_ride(ride_id: str, db: Session = Depends(get_db)):
    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
    if not db_ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return {
        "id": db_ride.id,
        "rider_id": db_ride.rider_id,
        "driver_id": db_ride.driver_id,
        "pickup_location": db_ride.pickup_location,
        "dropoff_location": db_ride.dropoff_location,
        "status": str(db_ride.status.value),
        "estimated_price": db_ride.estimated_price,
        "actual_price": db_ride.actual_price,
        "distance": db_ride.distance,
        "duration": db_ride.duration,
        "requested_at": db_ride.requested_at.isoformat() if db_ride.requested_at else None,
        "accepted_at": db_ride.accepted_at.isoformat() if db_ride.accepted_at else None,
        "started_at": db_ride.started_at.isoformat() if db_ride.started_at else None,
        "completed_at": db_ride.completed_at.isoformat() if db_ride.completed_at else None
    }

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
    db_ride.accepted_at = datetime.datetime.now()
    db.commit()

    await manager.broadcast_ride_update(ride_id, {
        "type": "ride_accepted",
        "data": {
            "ride_id": ride_id,
            "driver_id": driver_id,
            "driver_info": {
                "id": db_driver.id,
                "email": db_driver.email,
                "first_name": db_driver.first_name,
                "last_name": db_driver.last_name,
                "user_type": str(db_driver.user_type.value),
                "is_active": db_driver.is_active
            }
        }
    })

    return {"message": "Ride accepted successfully"}

@app.put("/rides/{ride_id}/start")
async def start_ride(ride_id: str, db: Session = Depends(get_db)):
    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
    if not db_ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    db_ride.status = RideStatus.IN_PROGRESS
    db_ride.started_at = datetime.datetime.now()
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
    db_ride.completed_at = datetime.datetime.now()
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
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "driverLocation":
                await manager.update_driver_location(user_id, message["location"])
            elif message["type"] == "rideRequest":
                nearby_drivers = manager._get_nearby_drivers(message["pickup"])
                await websocket.send_json({
                    "type": "nearbyDrivers",
                    "drivers": nearby_drivers
                })
            elif message["type"] == "rideStatus":
                await manager.broadcast_ride_update(
                    message["rideId"],
                    {"type": "rideStatus", "status": message["status"]}
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.get("/nearby-drivers")
async def get_nearby_drivers(lat: float, lng: float, radius_km: float = 5.0):
    location = {"lat": lat, "lng": lng}
    nearby_drivers = manager._get_nearby_drivers(location, radius_km)
    return {"drivers": nearby_drivers}

@app.post("/payments/", response_model=dict)
async def create_payment(payment: dict, db: Session = Depends(get_db)):
    db_payment = DBPayment(**payment)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return payment

@app.post("/ratings/", response_model=dict)
async def create_rating(rating: dict, db: Session = Depends(get_db)):
    db_rating = DBRating(**rating)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return rating

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
