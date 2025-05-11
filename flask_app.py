from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import os
import json
import time
import math
import random
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Mock database (in a real app, this would be PostgreSQL)
# Users collection
users = {
    "user123": {
        "id": "user123",
        "email": "customer@example.com",
        "password_hash": "hashed_password",  # In a real app, this would be properly hashed
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
        "user_type": "customer",
        "created_at": "2023-05-01T12:00:00Z"
    },
    "driver123": {
        "id": "driver123",
        "email": "driver@example.com",
        "password_hash": "hashed_password",  # In a real app, this would be properly hashed
        "first_name": "John",
        "last_name": "Driver",
        "phone_number": "9876543210",
        "user_type": "driver",
        "vehicle_info": {
            "model": "Toyota Camry",
            "color": "Black",
            "plate_number": "ABC-123"
        },
        "current_location": {
            "lat": 31.5204,
            "lng": 74.3587
        },
        "is_available": True,
        "rating": 4.8,
        "created_at": "2023-05-01T12:00:00Z"
    },
    "admin123": {
        "id": "admin123",
        "email": "admin@example.com",
        "password_hash": "hashed_password",  # In a real app, this would be properly hashed
        "first_name": "Admin",
        "last_name": "User",
        "phone_number": "5555555555",
        "user_type": "admin",
        "created_at": "2023-05-01T12:00:00Z"
    }
}

# Rides collection
rides = {
    "ride123": {
        "id": "ride123",
        "customer_id": "user123",
        "driver_id": "driver123",
        "pickup_location": {
            "address": "Mall Road, Lahore",
            "lat": 31.5604,
            "lng": 74.3287
        },
        "dropoff_location": {
            "address": "Gulberg, Lahore",
            "lat": 31.5204,
            "lng": 74.3587
        },
        "status": "completed",
        "fare": 250.50,
        "distance": 5.2,  # km
        "duration": 15,   # minutes
        "created_at": "2023-05-10T12:30:00Z",
        "completed_at": "2023-05-10T12:45:00Z"
    },
    "ride124": {
        "id": "ride124",
        "customer_id": "user123",
        "driver_id": None,
        "pickup_location": {
            "address": "Liberty Market, Lahore",
            "lat": 31.5104,
            "lng": 74.3487
        },
        "dropoff_location": {
            "address": "Johar Town, Lahore",
            "lat": 31.4704,
            "lng": 74.2787
        },
        "status": "pending",
        "fare": None,
        "distance": 7.5,  # km
        "duration": None,
        "created_at": "2023-05-11T10:15:00Z",
        "completed_at": None
    }
}

# Active drivers with their current locations
active_drivers = {
    "driver123": {
        "id": "driver123",
        "name": "John Driver",
        "vehicle": "Toyota Camry",
        "rating": 4.8,
        "location": {"lat": 31.5204, "lng": 74.3587},
        "is_available": True
    },
    "driver124": {
        "id": "driver124",
        "name": "Jane Driver",
        "vehicle": "Honda Civic",
        "rating": 4.6,
        "location": {"lat": 31.5304, "lng": 74.3487},
        "is_available": True
    },
    "driver125": {
        "id": "driver125",
        "name": "Mike Driver",
        "vehicle": "Suzuki Swift",
        "rating": 4.9,
        "location": {"lat": 31.5104, "lng": 74.3687},
        "is_available": True
    }
}

# Token verification middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # In a real app, verify the token
        # For now, just check if it's our mock token
        if token != 'mock_token_12345':
            return jsonify({'message': 'Invalid token'}), 401
        
        # In a real app, decode the token to get the user
        # For now, just return a mock user
        return f(*args, **kwargs)
    
    return decorated

# Helper functions
def calculate_distance(lat1, lng1, lat2, lng2):
    # Simple Haversine formula to calculate distance between two points
    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLng = math.radians(lng2 - lng1)
    a = (math.sin(dLat/2) * math.sin(dLat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLng/2) * math.sin(dLng/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

def calculate_fare(distance, duration, surge_factor=1.0):
    # Simple fare calculation
    base_fare = 100  # Base fare in PKR
    per_km_rate = 20  # Rate per km in PKR
    per_min_rate = 5  # Rate per minute in PKR
    
    fare = (base_fare + (distance * per_km_rate) + (duration * per_min_rate)) * surge_factor
    return round(fare, 2)

def get_nearby_drivers(lat, lng, radius_km=5.0):
    nearby = []
    for driver_id, driver in active_drivers.items():
        if driver["is_available"]:
            distance = calculate_distance(lat, lng, driver["location"]["lat"], driver["location"]["lng"])
            if distance <= radius_km:
                driver_info = driver.copy()
                driver_info["distance"] = round(distance, 2)
                nearby.append(driver_info)
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance"])
    return nearby

def generate_id():
    # Simple ID generator
    return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100, 999)}"

# Basic route for testing
@app.route('/')
def home():
    return jsonify({"message": "Fleet Management System API is running"})

# Auth routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # In a real app, validate credentials against database
    # For demo, accept any email with "customer", "driver", or "admin"
    user_type = None
    user_id = None
    
    for uid, user in users.items():
        if user["email"] == email:
            # In a real app, verify password hash
            user_type = user["user_type"]
            user_id = uid
            break
    
    if not user_type:
        if "customer" in email:
            user_type = "customer"
            user_id = "user123"
        elif "driver" in email:
            user_type = "driver"
            user_id = "driver123"
        elif "admin" in email:
            user_type = "admin"
            user_id = "admin123"
        else:
            user_type = "customer"  # Default
            user_id = "user123"
    
    user_data = users.get(user_id, {
        "id": user_id,
        "email": email,
        "first_name": "Test",
        "last_name": "User",
        "user_type": user_type
    })
    
    return jsonify({
        "token": "mock_token_12345",
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "user_type": user_data["user_type"],
            "first_name": user_data.get("first_name", "Test"),
            "last_name": user_data.get("last_name", "User")
        }
    })

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    user_type = data.get('user_type', 'customer')
    
    # In a real app, validate data and save to database
    # For demo, just return success
    
    user_id = generate_id()
    
    return jsonify({
        "token": "mock_token_12345",
        "user": {
            "id": user_id,
            "email": email,
            "user_type": user_type,
            "first_name": first_name,
            "last_name": last_name
        }
    })

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    # In a real app, get user from token
    # For demo, return a mock user based on Authorization header
    
    auth_header = request.headers.get('Authorization', '')
    user_type = "customer"  # Default
    
    if "driver" in auth_header.lower():
        user_type = "driver"
        user_data = users.get("driver123")
    elif "admin" in auth_header.lower():
        user_type = "admin"
        user_data = users.get("admin123")
    else:
        user_data = users.get("user123")
    
    if not user_data:
        user_data = {
            "id": "user123",
            "email": "customer@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
            "user_type": user_type
        }
    
    return jsonify(user_data)

# User profile routes
@app.route('/api/users/profile', methods=['GET'])
@token_required
def get_profile():
    # In a real app, get user from token
    # For demo, return a mock profile
    
    return jsonify({
        "id": "user123",
        "email": "customer@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
        "profile_picture": "https://via.placeholder.com/150",
        "created_at": "2023-05-01T12:00:00Z"
    })

@app.route('/api/users/profile', methods=['PUT'])
@token_required
def update_profile():
    data = request.json
    
    # In a real app, update user in database
    # For demo, just return success
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": "user123",
            "email": data.get("email", "customer@example.com"),
            "first_name": data.get("first_name", "Test"),
            "last_name": data.get("last_name", "User"),
            "phone_number": data.get("phone_number", "1234567890"),
            "profile_picture": data.get("profile_picture", "https://via.placeholder.com/150")
        }
    })

# Ride routes
@app.route('/api/rides', methods=['POST'])
@token_required
def create_ride():
    data = request.json
    
    pickup_lat = data.get('pickup_lat')
    pickup_lng = data.get('pickup_lng')
    dropoff_lat = data.get('dropoff_lat')
    dropoff_lng = data.get('dropoff_lng')
    pickup_address = data.get('pickup_address', 'Unknown Location')
    dropoff_address = data.get('dropoff_address', 'Unknown Location')
    
    if not all([pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]):
        return jsonify({"error": "Missing required location data"}), 400
    
    # Calculate distance and estimated duration
    distance = calculate_distance(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
    # Rough estimate: 2 minutes per km
    duration = int(distance * 2)
    
    # Calculate estimated fare
    estimated_fare = calculate_fare(distance, duration)
    
    # Create ride object
    ride_id = f"ride-{generate_id()}"
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    new_ride = {
        "id": ride_id,
        "customer_id": "user123",  # In a real app, get from token
        "driver_id": None,
        "pickup_location": {
            "address": pickup_address,
            "lat": pickup_lat,
            "lng": pickup_lng
        },
        "dropoff_location": {
            "address": dropoff_address,
            "lat": dropoff_lat,
            "lng": dropoff_lng
        },
        "status": "pending",
        "estimated_fare": estimated_fare,
        "actual_fare": None,
        "distance": round(distance, 2),
        "estimated_duration": duration,
        "actual_duration": None,
        "created_at": now,
        "accepted_at": None,
        "started_at": None,
        "completed_at": None
    }
    
    # In a real app, save to database
    rides[ride_id] = new_ride
    
    # Find nearby drivers
    nearby_drivers = get_nearby_drivers(pickup_lat, pickup_lng)
    
    return jsonify({
        "ride": new_ride,
        "nearby_drivers": nearby_drivers
    })

@app.route('/api/rides', methods=['GET'])
@token_required
def get_rides():
    # In a real app, filter by user from token
    # For demo, return all rides
    
    # Convert dictionary to list
    rides_list = list(rides.values())
    
    # Sort by created_at (newest first)
    rides_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    return jsonify(rides_list)

@app.route('/api/rides/<ride_id>', methods=['GET'])
@token_required
def get_ride(ride_id):
    ride = rides.get(ride_id)
    
    if not ride:
        return jsonify({"error": "Ride not found"}), 404
    
    return jsonify(ride)

@app.route('/api/rides/<ride_id>/accept', methods=['POST'])
@token_required
def accept_ride(ride_id):
    data = request.json
    driver_id = data.get('driver_id')
    
    if not driver_id:
        return jsonify({"error": "Driver ID is required"}), 400
    
    ride = rides.get(ride_id)
    
    if not ride:
        return jsonify({"error": "Ride not found"}), 404
    
    if ride["status"] != "pending":
        return jsonify({"error": "Ride is not in pending state"}), 400
    
    # Update ride status
    ride["status"] = "accepted"
    ride["driver_id"] = driver_id
    ride["accepted_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # In a real app, update in database
    rides[ride_id] = ride
    
    return jsonify(ride)

@app.route('/api/rides/<ride_id>/start', methods=['POST'])
@token_required
def start_ride(ride_id):
    ride = rides.get(ride_id)
    
    if not ride:
        return jsonify({"error": "Ride not found"}), 404
    
    if ride["status"] != "accepted":
        return jsonify({"error": "Ride is not in accepted state"}), 400
    
    # Update ride status
    ride["status"] = "in_progress"
    ride["started_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # In a real app, update in database
    rides[ride_id] = ride
    
    return jsonify(ride)

@app.route('/api/rides/<ride_id>/complete', methods=['POST'])
@token_required
def complete_ride(ride_id):
    ride = rides.get(ride_id)
    
    if not ride:
        return jsonify({"error": "Ride not found"}), 404
    
    if ride["status"] != "in_progress":
        return jsonify({"error": "Ride is not in progress"}), 400
    
    # Calculate actual duration and fare
    now = datetime.now()
    started_time = datetime.strptime(ride["started_at"], "%Y-%m-%dT%H:%M:%SZ")
    actual_duration = int((now - started_time).total_seconds() / 60)  # in minutes
    
    actual_fare = calculate_fare(ride["distance"], actual_duration)
    
    # Update ride status
    ride["status"] = "completed"
    ride["completed_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    ride["actual_duration"] = actual_duration
    ride["actual_fare"] = actual_fare
    
    # In a real app, update in database
    rides[ride_id] = ride
    
    return jsonify(ride)

@app.route('/api/rides/<ride_id>/cancel', methods=['POST'])
@token_required
def cancel_ride(ride_id):
    ride = rides.get(ride_id)
    
    if not ride:
        return jsonify({"error": "Ride not found"}), 404
    
    if ride["status"] in ["completed", "cancelled"]:
        return jsonify({"error": "Ride cannot be cancelled"}), 400
    
    # Update ride status
    ride["status"] = "cancelled"
    
    # In a real app, update in database
    rides[ride_id] = ride
    
    return jsonify(ride)

# Driver routes
@app.route('/api/drivers/nearby', methods=['GET'])
def get_nearby_drivers_api():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=5.0, type=float)
    
    if not lat or not lng:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    nearby = get_nearby_drivers(lat, lng, radius)
    
    return jsonify(nearby)

@app.route('/api/drivers/location', methods=['PUT'])
@token_required
def update_driver_location():
    data = request.json
    lat = data.get('lat')
    lng = data.get('lng')
    driver_id = data.get('driver_id')
    
    if not all([lat, lng, driver_id]):
        return jsonify({"error": "Missing required data"}), 400
    
    # Update driver location
    if driver_id in active_drivers:
        active_drivers[driver_id]["location"] = {"lat": lat, "lng": lng}
    
    return jsonify({"message": "Location updated successfully"})

@app.route('/api/drivers/availability', methods=['PUT'])
@token_required
def update_driver_availability():
    data = request.json
    is_available = data.get('is_available')
    driver_id = data.get('driver_id')
    
    if is_available is None or not driver_id:
        return jsonify({"error": "Missing required data"}), 400
    
    # Update driver availability
    if driver_id in active_drivers:
        active_drivers[driver_id]["is_available"] = is_available
    
    return jsonify({"message": "Availability updated successfully"})

# Payment routes (mock)
@app.route('/api/payments', methods=['POST'])
@token_required
def create_payment():
    data = request.json
    ride_id = data.get('ride_id')
    amount = data.get('amount')
    payment_method = data.get('payment_method', 'card')
    
    if not all([ride_id, amount]):
        return jsonify({"error": "Missing required data"}), 400
    
    # In a real app, process payment through payment gateway
    # For demo, just return success
    
    payment_id = f"payment-{generate_id()}"
    
    return jsonify({
        "id": payment_id,
        "ride_id": ride_id,
        "amount": amount,
        "payment_method": payment_method,
        "status": "completed",
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    })

# Rating routes
@app.route('/api/ratings', methods=['POST'])
@token_required
def create_rating():
    data = request.json
    ride_id = data.get('ride_id')
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not all([ride_id, rating]):
        return jsonify({"error": "Missing required data"}), 400
    
    if not 1 <= rating <= 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400
    
    # In a real app, save rating to database
    # For demo, just return success
    
    rating_id = f"rating-{generate_id()}"
    
    return jsonify({
        "id": rating_id,
        "ride_id": ride_id,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    })

# Admin routes
@app.route('/api/admin/users', methods=['GET'])
@token_required
def get_all_users():
    # In a real app, verify admin role
    # For demo, just return all users
    
    return jsonify(list(users.values()))

@app.route('/api/admin/rides', methods=['GET'])
@token_required
def get_all_rides():
    # In a real app, verify admin role
    # For demo, just return all rides
    
    return jsonify(list(rides.values()))

@app.route('/api/admin/drivers', methods=['GET'])
@token_required
def get_all_drivers():
    # In a real app, verify admin role
    # For demo, just return all active drivers
    
    return jsonify(list(active_drivers.values()))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port) 