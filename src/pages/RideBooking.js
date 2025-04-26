import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Slider,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
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

const RideBooking = () => {
  const { nearbyDrivers, updateLocation, subscribeToRide } = useWebSocket();
  const [pickup, setPickup] = useState('');
  const [destination, setDestination] = useState('');
  const [priceRange, setPriceRange] = useState([0, 1000]);
  const [route, setRoute] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [estimatedPrice, setEstimatedPrice] = useState(0);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const mapRef = useRef();

  const calculateRoute = async () => {
    if (!pickup || !destination) return;

    setIsLoading(true);
    try {
      // Use OpenRouteService API for routing
      const response = await axios.get(
        `https://api.openrouteservice.org/v2/directions/driving-car`,
        {
          params: {
            api_key: 'YOUR_OPENROUTESERVICE_API_KEY',
            start: `${pickup.split(',')[1]},${pickup.split(',')[0]}`,
            end: `${destination.split(',')[1]},${destination.split(',')[0]}`,
          },
        }
      );

      const routeData = response.data;
      setRoute(routeData);
      
      // Calculate estimated price based on distance
      const distance = routeData.routes[0].summary.distance / 1000; // Convert to km
      const price = distance * 20; // 20 PKR per km
      setEstimatedPrice(price);
    } catch (error) {
      console.error('Error calculating route:', error);
    }
    setIsLoading(false);
  };

  const handleBookRide = async () => {
    if (!selectedDriver) return;

    try {
      const response = await axios.post('http://localhost:8000/rides/', {
        rider_id: localStorage.getItem('userId'),
        pickup_location: {
          address: pickup,
          lat: route.routes[0].geometry.coordinates[0][1],
          lng: route.routes[0].geometry.coordinates[0][0],
        },
        dropoff_location: {
          address: destination,
          lat: route.routes[0].geometry.coordinates[route.routes[0].geometry.coordinates.length - 1][1],
          lng: route.routes[0].geometry.coordinates[route.routes[0].geometry.coordinates.length - 1][0],
        },
        estimated_price: estimatedPrice,
        distance: route.routes[0].summary.distance / 1000,
        duration: Math.ceil(route.routes[0].summary.duration / 60),
      });

      subscribeToRide(response.data.id);
    } catch (error) {
      console.error('Error booking ride:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Book a Ride
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              label="Pickup Location (lat,lng)"
              value={pickup}
              onChange={(e) => setPickup(e.target.value)}
              placeholder="31.5204,74.3587"
            />
            <TextField
              fullWidth
              label="Destination (lat,lng)"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="31.5204,74.3587"
            />
          </Box>
          <Box sx={{ mb: 2 }}>
            <Typography gutterBottom>Price Range (PKR)</Typography>
            <Slider
              value={priceRange}
              onChange={(e, newValue) => setPriceRange(newValue)}
              valueLabelDisplay="auto"
              min={0}
              max={1000}
            />
          </Box>
          <Button
            variant="contained"
            onClick={calculateRoute}
            disabled={!pickup || !destination}
          >
            Calculate Route
          </Button>
        </CardContent>
      </Card>

      <MapContainer
        center={center}
        zoom={12}
        style={{ height: '400px', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {nearbyDrivers.map((driver) => (
          <Marker
            key={driver.driver_id}
            position={[driver.location.lat, driver.location.lng]}
            eventHandlers={{
              click: () => setSelectedDriver(driver),
            }}
          >
            <Popup>
              Driver {driver.driver_id}
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {estimatedPrice > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Ride Details
            </Typography>
            <Typography>Estimated Price: PKR {estimatedPrice.toFixed(2)}</Typography>
            <Typography>
              Distance: {(route?.routes[0].summary.distance / 1000).toFixed(2)} km
            </Typography>
            <Typography>
              Duration: {Math.ceil(route?.routes[0].summary.duration / 60)} minutes
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleBookRide}
              disabled={!selectedDriver}
              sx={{ mt: 2 }}
            >
              Book Ride
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default RideBooking; 