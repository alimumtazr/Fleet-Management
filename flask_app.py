from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Basic route for testing
@app.route('/')
def home():
    return jsonify({"message": "Ride Service API is running"})

# Auth routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    # In a real app, you would validate credentials here
    # For now, return a mock response with the format expected by the frontend
    return jsonify({
        "token": "mock_token_12345",
        "user": {
            "id": "user123",
            "email": data.get("email", "user@example.com"),
            "user_type": "customer",  # Changed from 'role' to 'user_type' to match frontend expectation
            "first_name": "Test",
            "last_name": "User"
        }
    })

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    # In a real app, you would create a new user here
    # For now, return a mock response with the format expected by the frontend
    return jsonify({
        "token": "mock_token_12345",
        "user": {
            "id": "user123",
            "email": data.get("email", "user@example.com"),
            "user_type": "customer",  # Changed from 'role' to 'user_type' to match frontend expectation
            "first_name": data.get("first_name", "Test"),
            "last_name": data.get("last_name", "User")
        }
    })

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    # In a real app, you would validate the token and return the user
    # For now, return a mock response with the format expected by the frontend
    return jsonify({
        "id": "user123",
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
        "user_type": "customer"  # Changed from 'role' to 'user_type' to match frontend expectation
    })

# Ride routes
@app.route('/rides', methods=['POST'])
def create_ride():
    data = request.json
    # In a real app, you would create a new ride here
    # For now, return a mock response
    return jsonify({
        "success": True,
        "message": "Ride created successfully",
        "data": {
            "id": "ride123",
            "pickup_location": data.get("pickup_location"),
            "dropoff_location": data.get("dropoff_location"),
            "status": "pending"
        }
    })

@app.route('/rides', methods=['GET'])
def get_rides():
    # In a real app, you would fetch rides from the database
    # For now, return mock data
    return jsonify({
        "success": True,
        "data": [
            {
                "id": "ride123",
                "pickup_location": "Location A",
                "dropoff_location": "Location B",
                "status": "completed",
                "fare": 25.50,
                "created_at": "2023-05-10T12:30:00Z"
            },
            {
                "id": "ride124",
                "pickup_location": "Location C",
                "dropoff_location": "Location D",
                "status": "pending",
                "created_at": "2023-05-11T10:15:00Z"
            }
        ]
    })

# Driver routes
@app.route('/nearby-drivers', methods=['GET'])
def get_nearby_drivers():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    # In a real app, you would find nearby drivers
    # For now, return mock data
    return jsonify({
        "success": True,
        "data": [
            {
                "id": "driver1",
                "name": "John Driver",
                "vehicle": "Toyota Camry",
                "rating": 4.8,
                "location": {"lat": lat + 0.01, "lng": lng - 0.01},
                "distance": 1.2
            },
            {
                "id": "driver2",
                "name": "Jane Driver",
                "vehicle": "Honda Civic",
                "rating": 4.6,
                "location": {"lat": lat - 0.02, "lng": lng + 0.02},
                "distance": 2.5
            }
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port) 