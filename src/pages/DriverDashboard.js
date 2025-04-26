import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const center = [31.5204, 74.3587]; // Default to Islamabad

const DriverDashboard = () => {
  const { updateLocation, currentRide } = useWebSocket();
  const [isOnline, setIsOnline] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [rideRequests, setRideRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Get current location
    if (navigator.geolocation) {
      navigator.geolocation.watchPosition(
        (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setCurrentLocation([location.lat, location.lng]);
          if (isOnline) {
            updateLocation(location);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
        },
        { enableHighAccuracy: true }
      );
    }
  }, [isOnline, updateLocation]);

  const handleToggleOnline = async () => {
    setIsOnline(!isOnline);
    if (!isOnline && currentLocation) {
      updateLocation({ lat: currentLocation[0], lng: currentLocation[1] });
    }
  };

  const handleAcceptRide = async (rideId) => {
    try {
      setIsLoading(true);
      await axios.put(`http://localhost:8000/rides/${rideId}/accept`, {
        driver_id: localStorage.getItem('userId'),
      });
      setRideRequests(requests => requests.filter(req => req.id !== rideId));
    } catch (error) {
      console.error('Error accepting ride:', error);
    }
    setIsLoading(false);
  };

  const handleStartRide = async (rideId) => {
    try {
      setIsLoading(true);
      await axios.put(`http://localhost:8000/rides/${rideId}/start`);
    } catch (error) {
      console.error('Error starting ride:', error);
    }
    setIsLoading(false);
  };

  const handleCompleteRide = async (rideId) => {
    try {
      setIsLoading(true);
      await axios.put(`http://localhost:8000/rides/${rideId}/complete`);
    } catch (error) {
      console.error('Error completing ride:', error);
    }
    setIsLoading(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5">Driver Dashboard</Typography>
            <Button
              variant="contained"
              color={isOnline ? 'error' : 'success'}
              onClick={handleToggleOnline}
            >
              {isOnline ? 'Go Offline' : 'Go Online'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      <MapContainer
        center={currentLocation || center}
        zoom={12}
        style={{ height: '400px', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {currentLocation && (
          <Marker position={currentLocation}>
            <Popup>Your Current Location</Popup>
          </Marker>
        )}
      </MapContainer>

      {currentRide && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Ride
            </Typography>
            <Typography>Status: {currentRide.status}</Typography>
            <Typography>Pickup: {currentRide.pickup_location.address}</Typography>
            <Typography>Destination: {currentRide.dropoff_location.address}</Typography>
            <Box sx={{ mt: 2 }}>
              {currentRide.status === 'ride_accepted' && (
                <Button
                  variant="contained"
                  onClick={() => handleStartRide(currentRide.ride_id)}
                  disabled={isLoading}
                >
                  Start Ride
                </Button>
              )}
              {currentRide.status === 'ride_started' && (
                <Button
                  variant="contained"
                  color="success"
                  onClick={() => handleCompleteRide(currentRide.ride_id)}
                  disabled={isLoading}
                >
                  Complete Ride
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {rideRequests.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Ride Requests
            </Typography>
            <List>
              {rideRequests.map((request) => (
                <React.Fragment key={request.id}>
                  <ListItem>
                    <ListItemText
                      primary={`From: ${request.pickup_location.address}`}
                      secondary={`To: ${request.dropoff_location.address}`}
                    />
                    <Button
                      variant="contained"
                      onClick={() => handleAcceptRide(request.id)}
                      disabled={isLoading}
                    >
                      Accept
                    </Button>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <CircularProgress />
        </Box>
      )}
    </Box>
  );
};

export default DriverDashboard; 