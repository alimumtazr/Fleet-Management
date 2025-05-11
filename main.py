from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import UserType, RideStatus, User as DBUser, Ride as DBRide, Payment as DBPayment, Rating as DBRating
from realtime_service import manager
import json
from datetime import timedelta, now, timezone
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
import math

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

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    heading: Optional[float] = 0
    speed: Optional[float] = 0

class RideRequestCreate(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: Optional[str] = None
    dropoff_latitude: float
    dropoff_longitude: float
    dropoff_address: Optional[str] = None
    
class DriverRideResponse(BaseModel):
    request_id: str
    accept: bool

class NotificationResponse(BaseModel):
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    unread_only: Optional[bool] = False

@app.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Debug print statements
        print(f"Received user_type: {user.user_type}")
        print(f"Available UserType values: {[member.name for member in UserType]}")
        
        # Validate user_type
        try:
            # Convert user_type string to enum - this will raise ValueError if invalid
            user_type_enum = UserType[user.user_type.upper()]
            print(f"Converted to enum: {user_type_enum}")
        except (KeyError, ValueError) as e:
            print(f"Invalid user_type: {user.user_type}. Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user type: {user.user_type}. Valid types are: {', '.join([t.value for t in UserType])}"
            )
        
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
            user_type=user_type_enum,  # Use the validated enum
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
        # Debug print statements
        print(f"Received user_type: {user.user_type}")
        print(f"Available UserType values: {[member.name for member in UserType]}")
        
        # Validate user_type
        try:
            # Convert user_type string to enum - this will raise ValueError if invalid
            user_type_enum = UserType[user.user_type.upper()]
            print(f"Converted to enum: {user_type_enum}")
        except (KeyError, ValueError) as e:
            print(f"Invalid user_type: {user.user_type}. Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user type: {user.user_type}. Valid types are: {', '.join([t.value for t in UserType])}"
            )
        
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
            user_type=user_type_enum,
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
        "user_type": str(current_user.user_type.value),
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
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time communication
    Message types:
    - driver_location: update driver location
    - ride_request: request a ride
    - subscribe_to_rides: driver subscribes to receive ride requests
    - cancel_ride_request: cancel a ride request
    - subscribe_to_ride: subscribe to updates for a specific ride
    - update_ride_status: update ride status
    """
    await manager.connect(websocket, user_id)
    try:
        # Set client state to track the user ID
        if not hasattr(websocket, "client_state"):
            websocket.client_state = {}
        websocket.client_state["user_id"] = user_id
        
        # Check if user exists and is active
        db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not db_user or not db_user.is_active:
            await websocket.send_json({
                "type": "error",
                "message": "User not found or inactive"
            })
            await websocket.close()
            return
            
        # Send initial state
        await websocket.send_json({
            "type": "connection_established",
            "user_id": user_id,
            "user_type": str(db_user.user_type.value)
        })
        
        # Main message loop
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type", "")
                
                # Process based on message type
                if message_type == "driver_location":
                    # Update driver location
                    if db_user.user_type != UserType.DRIVER:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Only drivers can update location"
                        })
                        continue
                        
                    location = message.get("location", {})
                    if not location or "lat" not in location or "lng" not in location:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid location data"
                        })
                        continue
                        
                    # Update in database
                    db_user.current_latitude = location["lat"]
                    db_user.current_longitude = location["lng"]
                    db_user.updated_at = datetime.now(timezone.utc)
                    db.commit()
                    
                    # Update in real-time service
                    await manager.update_driver_location(user_id, location)
                    
                    await websocket.send_json({
                        "type": "location_updated"
                    })
                    
                elif message_type == "subscribe_to_rides":
                    # Driver subscribes to receive ride requests
                    if db_user.user_type != UserType.DRIVER:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Only drivers can subscribe to ride requests"
                        })
                        continue
                        
                    # Update driver availability
                    db_user.is_available = True
                    db.commit()
                    
                    # Subscribe to ride requests
                    await manager.subscribe_to_rides(user_id)
                    
                    await websocket.send_json({
                        "type": "subscribed_to_rides"
                    })
                    
                elif message_type == "unsubscribe_from_rides":
                    # Driver unsubscribes from ride requests
                    if db_user.user_type != UserType.DRIVER:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Only drivers can unsubscribe from ride requests"
                        })
                        continue
                        
                    # Update driver availability
                    db_user.is_available = False
                    db.commit()
                    
                    # Handled by disconnect
                    await websocket.send_json({
                        "type": "unsubscribed_from_rides"
                    })
                    
                elif message_type == "subscribe_to_ride":
                    # Subscribe to updates for a specific ride
                    ride_id = message.get("ride_id")
                    if not ride_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Missing ride_id"
                        })
                        continue
                        
                    # Check if user is part of this ride
                    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
                    if not db_ride or (str(db_ride.rider_id) != user_id and str(db_ride.driver_id) != user_id):
                        await websocket.send_json({
                            "type": "error",
                            "message": "You are not part of this ride"
                        })
                        continue
                        
                    # Subscribe to ride updates
                    ride_channel = f"ride_{ride_id}"
                    await manager.subscribe_to_ride_updates(ride_channel, websocket)
                    
                    await websocket.send_json({
                        "type": "subscribed_to_ride",
                        "ride_id": ride_id
                    })
                    
                elif message_type == "update_ride_status":
                    # Update ride status (for driver)
                    ride_id = message.get("ride_id")
                    status = message.get("status")
                    
                    if not ride_id or not status:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Missing ride_id or status"
                        })
                        continue
                        
                    # Check if driver is assigned to this ride
                    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
                    if not db_ride or str(db_ride.driver_id) != user_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "You are not the driver of this ride"
                        })
                        continue
                        
                    # Update ride status
                    if status == "started":
                        if db_ride.status != RideStatus.ACCEPTED:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Cannot start ride with status {db_ride.status}"
                            })
                            continue
                            
                        db_ride.status = RideStatus.IN_PROGRESS
                        db_ride.started_at = datetime.now(timezone.utc)
                        
                    elif status == "arrived":
                        if db_ride.status != RideStatus.ACCEPTED:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Cannot mark arrival for ride with status {db_ride.status}"
                            })
                            continue
                            
                        db_ride.driver_arrived_at = datetime.now(timezone.utc)
                        
                    elif status == "completed":
                        if db_ride.status != RideStatus.IN_PROGRESS:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Cannot complete ride with status {db_ride.status}"
                            })
                            continue
                            
                        db_ride.status = RideStatus.COMPLETED
                        db_ride.completed_at = datetime.now(timezone.utc)
                        
                        # Update driver's total rides
                        db_user.total_rides += 1
                        
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Invalid status: {status}"
                        })
                        continue
                        
                    db.commit()
                    
                    # Broadcast to all ride subscribers
                    status_data = {
                        "type": f"ride_{status}",
                        "ride_id": ride_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Add driver location for 'started' and 'arrived' events
                    if status in ["started", "arrived"]:
                        status_data["location"] = {
                            "lat": db_user.current_latitude,
                            "lng": db_user.current_longitude
                        }
                        
                    await manager.broadcast_ride_update(f"ride_{ride_id}", status_data)
                    
                    # Create notification for rider
                    notification_title = {
                        "started": "Ride Started",
                        "arrived": "Driver Arrived",
                        "completed": "Ride Completed"
                    }.get(status, "Ride Update")
                    
                    notification_message = {
                        "started": f"Your ride with {db_user.get_full_name()} has started",
                        "arrived": f"Driver {db_user.get_full_name()} has arrived at pickup location",
                        "completed": f"Your ride has been completed"
                    }.get(status, "Your ride status has been updated")
                    
                    notification_type = {
                        "started": NotificationType.RIDE_STARTED,
                        "arrived": NotificationType.DRIVER_ARRIVED,
                        "completed": NotificationType.RIDE_COMPLETED
                    }.get(status, NotificationType.SYSTEM_MESSAGE)
                    
                    db_notification = Notification(
                        user_id=str(db_ride.rider_id),
                        type=notification_type,
                        title=notification_title,
                        message=notification_message,
                        related_id=str(ride_id)
                    )
                    db.add(db_notification)
                    db.commit()
                    
                    await websocket.send_json({
                        "type": "ride_status_updated",
                        "ride_id": ride_id,
                        "status": status
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message"
                })
                
            except Exception as e:
                print(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(user_id)

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
        "user_type": str(current_user.user_type.value),
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
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time communication
    Message types:
    - driver_location: update driver location
    - ride_request: request a ride
    - subscribe_to_rides: driver subscribes to receive ride requests
    - cancel_ride_request: cancel a ride request
    - subscribe_to_ride: subscribe to updates for a specific ride
    - update_ride_status: update ride status
    """
    await manager.connect(websocket, user_id)
    try:
        # Set client state to track the user ID
        if not hasattr(websocket, "client_state"):
            websocket.client_state = {}
        websocket.client_state["user_id"] = user_id
        
        # Check if user exists and is active
        db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not db_user or not db_user.is_active:
            await websocket.send_json({
                "type": "error",
                "message": "User not found or inactive"
            })
            await websocket.close()
            return
            
        # Send initial state
        await websocket.send_json({
            "type": "connection_established",
            "user_id": user_id,
            "user_type": str(db_user.user_type.value)
        })
        
        # Main message loop
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type", "")
                
                # Process based on message type
                if message_type == "driver_location":
                    # Update driver location
                    if db_user.user_type != UserType.DRIVER:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Only drivers can update location"
                        })
                        continue
                        
                    location = message.get("location", {})
                    if not location or "lat" not in location or "lng" not in location:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid location data"
                        })
                        continue
                        
                    # Update in database
                    db_user.current_latitude = location["lat"]
                    db_user.current_longitude = location["lng"]
                    db_user.updated_at = datetime.now(timezone.utc)
                    db.commit()
                    
                    # Update in real-time service
                    await manager.update_driver_location(user_id, location)
                    
                    await websocket.send_json({
                        "type": "location_updated"
                    })
                    
                elif message_type == "subscribe_to_rides":
                    # Driver subscribes to receive ride requests
                    if db_user.user_type != UserType.DRIVER:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Only drivers can subscribe to ride requests"
                        })
                        continue
                        
                    # Update driver availability
                    db_user.is_available = True
                    db.commit()
                    
                    # Subscribe to ride requests
                    await manager.subscribe_to_rides(user_id)
                    
                    await websocket.send_json({
                        "type": "subscribed_to_rides"
                    })
                    
                elif message_type == "unsubscribe_from_rides":
                    # Driver unsubscribes from ride requests
                    if db_user.user_type != UserType.DRIVER:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Only drivers can unsubscribe from ride requests"
                        })
                        continue
                        
                    # Update driver availability
                    db_user.is_available = False
                    db.commit()
                    
                    # Handled by disconnect
                    await websocket.send_json({
                        "type": "unsubscribed_from_rides"
                    })
                    
                elif message_type == "subscribe_to_ride":
                    # Subscribe to updates for a specific ride
                    ride_id = message.get("ride_id")
                    if not ride_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Missing ride_id"
                        })
                        continue
                        
                    # Check if user is part of this ride
                    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
                    if not db_ride or (str(db_ride.rider_id) != user_id and str(db_ride.driver_id) != user_id):
                        await websocket.send_json({
                            "type": "error",
                            "message": "You are not part of this ride"
                        })
                        continue
                        
                    # Subscribe to ride updates
                    ride_channel = f"ride_{ride_id}"
                    await manager.subscribe_to_ride_updates(ride_channel, websocket)
                    
                    await websocket.send_json({
                        "type": "subscribed_to_ride",
                        "ride_id": ride_id
                    })
                    
                elif message_type == "update_ride_status":
                    # Update ride status (for driver)
                    ride_id = message.get("ride_id")
                    status = message.get("status")
                    
                    if not ride_id or not status:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Missing ride_id or status"
                        })
                        continue
                        
                    # Check if driver is assigned to this ride
                    db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
                    if not db_ride or str(db_ride.driver_id) != user_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "You are not the driver of this ride"
                        })
                        continue
                        
                    # Update ride status
                    if status == "started":
                        if db_ride.status != RideStatus.ACCEPTED:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Cannot start ride with status {db_ride.status}"
                            })
                            continue
                            
                        db_ride.status = RideStatus.IN_PROGRESS
                        db_ride.started_at = datetime.now(timezone.utc)
                        
                    elif status == "arrived":
                        if db_ride.status != RideStatus.ACCEPTED:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Cannot mark arrival for ride with status {db_ride.status}"
                            })
                            continue
                            
                        db_ride.driver_arrived_at = datetime.now(timezone.utc)
                        
                    elif status == "completed":
                        if db_ride.status != RideStatus.IN_PROGRESS:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Cannot complete ride with status {db_ride.status}"
                            })
                            continue
                            
                        db_ride.status = RideStatus.COMPLETED
                        db_ride.completed_at = datetime.now(timezone.utc)
                        
                        # Update driver's total rides
                        db_user.total_rides += 1
                        
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Invalid status: {status}"
                        })
                        continue
                        
                    db.commit()
                    
                    # Broadcast to all ride subscribers
                    status_data = {
                        "type": f"ride_{status}",
                        "ride_id": ride_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Add driver location for 'started' and 'arrived' events
                    if status in ["started", "arrived"]:
                        status_data["location"] = {
                            "lat": db_user.current_latitude,
                            "lng": db_user.current_longitude
                        }
                        
                    await manager.broadcast_ride_update(f"ride_{ride_id}", status_data)
                    
                    # Create notification for rider
                    notification_title = {
                        "started": "Ride Started",
                        "arrived": "Driver Arrived",
                        "completed": "Ride Completed"
                    }.get(status, "Ride Update")
                    
                    notification_message = {
                        "started": f"Your ride with {db_user.get_full_name()} has started",
                        "arrived": f"Driver {db_user.get_full_name()} has arrived at pickup location",
                        "completed": f"Your ride has been completed"
                    }.get(status, "Your ride status has been updated")
                    
                    notification_type = {
                        "started": NotificationType.RIDE_STARTED,
                        "arrived": NotificationType.DRIVER_ARRIVED,
                        "completed": NotificationType.RIDE_COMPLETED
                    }.get(status, NotificationType.SYSTEM_MESSAGE)
                    
                    db_notification = Notification(
                        user_id=str(db_ride.rider_id),
                        type=notification_type,
                        title=notification_title,
                        message=notification_message,
                        related_id=str(ride_id)
                    )
                    db.add(db_notification)
                    db.commit()
                    
                    await websocket.send_json({
                        "type": "ride_status_updated",
                        "ride_id": ride_id,
                        "status": status
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message"
                })
                
            except Exception as e:
                print(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(user_id)
):
    """
    Cancel a ride
    """
    try:
        # Get ride from DB
        db_ride = db.query(DBRide).filter(DBRide.id == ride_id).first()
        if not db_ride:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ride not found"
            )
        
        # Check if user is allowed to cancel this ride
        if str(current_user.id) != str(db_ride.rider_id) and str(current_user.id) != str(db_ride.driver_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to cancel this ride"
            )
        
        # Check if ride can be cancelled
        if db_ride.status in [RideStatus.COMPLETED, RideStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel a ride with status {db_ride.status}"
            )
        
        # Update ride status
        db_ride.status = RideStatus.CANCELLED
        db_ride.cancelled_at = datetime.now(timezone.utc)
        db_ride.cancellation_reason = cancellation_reason
        db_ride.cancelled_by = "rider" if str(current_user.id) == str(db_ride.rider_id) else "driver"
        db.commit()
        
        # Notify other party
        other_user_id = str(db_ride.driver_id) if str(current_user.id) == str(db_ride.rider_id) else str(db_ride.rider_id)
        if other_user_id in manager.active_connections:
            await manager.active_connections[other_user_id].send_json({
                'type': 'ride_cancelled',
                'ride_id': ride_id,
                'cancelled_by': db_ride.cancelled_by,
                'reason': cancellation_reason
            })
        
        # Create notification
        db_notification = Notification(
            user_id=other_user_id,
            type=NotificationType.RIDE_CANCELLED,
            title="Ride Cancelled",
            message=f"Your ride has been cancelled. Reason: {cancellation_reason}",
            related_id=str(ride_id)
        )
        db.add(db_notification)
        db.commit()
        
        # Broadcast to all subscribers
        await manager.broadcast_ride_update(f"ride_{ride_id}", {
            'type': 'ride_cancelled',
            'ride_id': ride_id,
            'cancelled_by': db_ride.cancelled_by,
            'reason': cancellation_reason
        })
        
        return {
            "status": "success",
            "message": "Ride cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error cancelling ride: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling ride: {str(e)}"
        )

# Get user's notifications
@app.get("/api/notifications")
async def get_notifications(
    params: NotificationResponse = Depends(),
    current_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user notifications
    """
    try:
        query = db.query(Notification).filter(Notification.user_id == current_user.id)
        if params.unread_only:
            query = query.filter(Notification.is_read == False)
        
        total = query.count()
        
        notifications = query.order_by(Notification.created_at.desc()) \
            .offset(params.offset).limit(params.limit).all()
        
        return {
            "status": "success",
            "total": total,
            "notifications": [
                {
                    "id": notification.id,
                    "type": notification.type.value,
                    "title": notification.title,
                    "message": notification.message,
                    "related_id": notification.related_id,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat()
                }
                for notification in notifications
            ]
        }
    except Exception as e:
        print(f"Error getting notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting notifications: {str(e)}"
        )

# Mark notifications as read
@app.post("/api/notifications/read")
async def mark_notifications_read(
    notification_ids: List[int],
    current_user: DBUser = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark notifications as read
    """
    try:
        # Only update notifications belonging to the current user
        db.query(Notification) \
            .filter(Notification.user_id == current_user.id) \
            .filter(Notification.id.in_(notification_ids)) \
            .update({Notification.is_read: True}, synchronize_session=False)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Marked {len(notification_ids)} notifications as read"
        }
    except Exception as e:
        db.rollback()
        print(f"Error marking notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notifications as read: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
