import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Grid,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import MapComponent from '../maps/MapComponent';
import { updateDriverLocation } from '../../store/slices/driverSlice';

// Geofence radius in meters (20km)
const GEOFENCE_RADIUS = 20000;

// Lahore city center coordinates
const CITY_CENTER = [31.5204, 74.3587];

const DriverTracking = ({ rideId }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [isWithinGeofence, setIsWithinGeofence] = useState(true);
  const { ride, customer } = useSelector((state) => state.rides);

  // Function to calculate distance between two points
  const calculateDistance = (point1, point2) => {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = (point1[0] * Math.PI) / 180;
    const φ2 = (point2[0] * Math.PI) / 180;
    const Δφ = ((point2[0] - point1[0]) * Math.PI) / 180;
    const Δλ = ((point2[1] - point1[1]) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  };

  // Check if location is within geofence
  const checkGeofence = useCallback((location) => {
    if (!location) return true;
    const distance = calculateDistance(CITY_CENTER, location);
    return distance <= GEOFENCE_RADIUS;
  }, []);

  // Update driver's location
  const updateLocation = useCallback(async (position) => {
    const { latitude, longitude } = position.coords;
    const location = [latitude, longitude];

    try {
      setLoading(true);
      setError(null);

      // Check if within geofence
      const withinGeofence = checkGeofence(location);
      setIsWithinGeofence(withinGeofence);

      if (!withinGeofence) {
        setError('Warning: You are outside the service area');
      }

      // Update location in state and redux store
      setCurrentLocation(location);
      await dispatch(updateDriverLocation({
        rideId,
        location,
        timestamp: new Date().toISOString(),
      })).unwrap();

    } catch (error) {
      setError('Failed to update location');
      console.error('Location update error:', error);
    } finally {
      setLoading(false);
    }
  }, [dispatch, rideId, checkGeofence]);

  // Watch driver's position
  useEffect(() => {
    let watchId;

    const startTracking = async () => {
      if ('geolocation' in navigator) {
        try {
          watchId = navigator.geolocation.watchPosition(
            updateLocation,
            (error) => {
              console.error('Geolocation error:', error);
              setError('Unable to access location. Please enable GPS.');
            },
            {
              enableHighAccuracy: true,
              timeout: 5000,
              maximumAge: 0,
            }
          );
        } catch (error) {
          console.error('Geolocation setup error:', error);
          setError('Failed to initialize location tracking');
        }
      } else {
        setError('Geolocation is not supported by your browser');
      }
    };

    startTracking();

    // Cleanup
    return () => {
      if (watchId) {
        navigator.geolocation.clearWatch(watchId);
      }
    };
  }, [updateLocation]);

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h5" gutterBottom className="gradient-text">
              Live Tracking
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
                {error}
              </Alert>
            )}

            {!isWithinGeofence && (
              <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
                You are outside the service area. Please return to Lahore city limits.
              </Alert>
            )}

            <Box sx={{ position: 'relative', mt: 2 }}>
              <MapComponent
                center={currentLocation || CITY_CENTER}
                driverLocation={currentLocation}
                customerLocation={ride?.pickup?.coordinates}
                geofence={{
                  center: CITY_CENTER,
                  radius: GEOFENCE_RADIUS,
                }}
                route={ride?.route}
              />
              {loading && (
                <CircularProgress
                  size={24}
                  sx={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                  }}
                />
              )}
            </Box>

            {ride && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Ride Details
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography color="text.secondary">Pickup</Typography>
                    <Typography variant="body1">
                      {ride.pickup?.description}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography color="text.secondary">Dropoff</Typography>
                    <Typography variant="body1">
                      {ride.dropoff?.description}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DriverTracking; 