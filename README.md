# Fleet Management System

A modern ride-hailing application similar to Uber, built with FastAPI for the backend and React for the frontend.

## Features

- 🚗 Real-time driver location tracking
- 🗺️ Interactive map integration
- 📱 Responsive design for mobile and desktop
- 💳 Multiple payment options
- ⭐ Rating system for drivers and riders
- 📊 Driver and rider dashboards
- 📝 Ride history and statistics
- 🔔 Real-time notifications

## Technology Stack

### Backend
- **FastAPI**: High-performance web framework for building APIs with Python
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **WebSockets**: Real-time communication between server and clients
- **JWT Authentication**: Secure authentication and authorization
- **SQLite**: Database for development (can be easily switched to PostgreSQL for production)

### Frontend
- **React**: Frontend library for building user interfaces
- **Material-UI**: React component library implementing Google's Material Design
- **React Router**: Navigation and routing
- **Redux Toolkit**: State management
- **Leaflet**: Interactive maps
- **Axios**: HTTP client for API requests

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fleet-management.git
cd fleet-management
```

2. Set up the backend:
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Run the backend server
uvicorn main:app --reload
```

3. Set up the frontend:
```bash
cd frontend
npm install
npm start
```

4. Access the application:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

### Test Accounts

For testing purposes, the following accounts are available:

| Role     | Email               | Password    |
|----------|---------------------|-------------|
| Admin    | admin@example.com   | admin123    |
| Driver   | driver@example.com  | driver123   |
| Customer | customer@example.com| customer123 |

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Backend configuration
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./app.db  # Or your PostgreSQL connection string
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend configuration
REACT_APP_API_URL=http://localhost:8000
```

## API Documentation

Once the backend server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Mobile App

A companion mobile app is planned for the future, which will provide native mobile experience for both drivers and riders.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/)
- [Leaflet](https://leafletjs.com/) 