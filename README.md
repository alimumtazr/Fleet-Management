# Ride-Hailing Application

A real-time ride-hailing application similar to Uber/Careem, built with FastAPI and React.

## Features

- Real-time driver tracking and location updates
- Interactive map interface for ride booking
- Price estimation and negotiation
- Driver-rider matching system
- Real-time ride status updates
- Payment integration
- Rating system
- Pakistan-specific map integration

## Tech Stack

### Backend
- FastAPI
- WebSocket for real-time communication
- PostgreSQL database
- SQLAlchemy ORM
- JWT authentication

### Frontend
- React
- Material-UI
- Google Maps API
- WebSocket client
- Axios for API calls

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following variables:
```
DATABASE_URL=postgresql://user:password@localhost:5432/ride_hailing
SECRET_KEY=your-secret-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create a `.env` file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

3. Start the development server:
```bash
npm start
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for the interactive API documentation.

## Key Features Implementation

### Real-time Location Updates
- WebSocket connection for continuous location updates
- Driver location broadcasting to nearby riders
- Real-time ride status updates

### Ride Booking Flow
1. Rider enters pickup and destination locations
2. System calculates route and estimated price
3. Nearby drivers are shown on the map
4. Rider can select a driver based on price and rating
5. Driver accepts/rejects the ride request
6. Real-time tracking during the ride
7. Payment processing upon completion

### Driver Features
- Online/offline status toggle
- Real-time location updates
- Ride request notifications
- Ride status management
- Earnings tracking

### Rider Features
- Real-time driver tracking
- Price estimation
- Ride history
- Rating system
- Payment methods

## Security Considerations

- JWT-based authentication
- Secure WebSocket connections
- Input validation
- Rate limiting
- Secure payment processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 