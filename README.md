# Fleet Management System (FMS)

A full-stack ride-hailing service application similar to Uber, built with Flask, React.js, and PostgreSQL.

## Features
- Real-time GPS tracking
- Dynamic pricing
- Ride pooling
- Driver incentives
- User authentication and authorization
- Real-time notifications

## Tech Stack
- Frontend: React.js
- Backend: Flask (Python)
- Database: PostgreSQL
- Real-time updates: WebSocket
- Maps Integration: Google Maps API

## Project Structure
```
fleet-management-system/
├── backend/               # Flask server
│   ├── app/
│   ├── config/
│   ├── migrations/
│   └── requirements.txt
│
├── frontend/             # React application
│   ├── public/
│   ├── src/
│   └── package.json
│
└── README.md
```

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

4. Run the Flask server:
   ```bash
   flask run
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm start
   ```

## Environment Variables
Create `.env` files in both frontend and backend directories with the following variables:

Backend (.env):
```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/fms_db
SECRET_KEY=your_secret_key
```

Frontend (.env):
```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 