import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Divider,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import MapComponent from '../maps/MapComponent';
import { calculateFare } from './fareCalculator';
import { bookRide } from '../../store/slices/rideSlice';
import LocationSearchInput from './LocationSearchInput';

const RideBooking = () => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rideDetails, setRideDetails] = useState({
    pickup: null,
    dropoff: null,
    distance: 0,
    duration: 0,
    fare: 0,
  });

  // Calculate fare when distance or duration changes
  useEffect(() => {
    if (rideDetails.distance && rideDetails.duration) {
      const fare = calculateFare(rideDetails.distance, rideDetails.duration);
      setRideDetails(prev => ({ ...prev, fare }));
    }
  }, [rideDetails.distance, rideDetails.duration]);

  const handleLocationSelect = async (type, location) => {
    try {
      setRideDetails(prev => ({
        ...prev,
        [type]: location,
      }));

      // If both locations are selected, calculate distance and duration
      if (type === 'dropoff' && rideDetails.pickup) {
        setLoading(true);
        const result = await calculateRoute(rideDetails.pickup, location);
        setRideDetails(prev => ({
          ...prev,
          distance: result.distance,
          duration: result.duration,
        }));
      }
    } catch (error) {
      setError('Error calculating route. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBookRide = async () => {
    try {
      setLoading(true);
      await dispatch(bookRide({
        ...rideDetails,
        customerId: user.id,
        status: 'pending',
        createdAt: new Date().toISOString(),
      })).unwrap();
      // Navigate to ride tracking page or show success message
    } catch (error) {
      setError('Failed to book ride. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h5" gutterBottom className="gradient-text">
              Book a Ride
            </Typography>
            
            <LocationSearchInput
              label="Pickup Location"
              onChange={(location) => handleLocationSelect('pickup', location)}
              sx={{ mt: 2 }}
            />

            <LocationSearchInput
              label="Dropoff Location"
              onChange={(location) => handleLocationSelect('dropoff', location)}
              sx={{ mt: 2 }}
            />

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            {rideDetails.fare > 0 && (
              <Box sx={{ mt: 3 }}>
                <Divider />
                <Typography variant="h6" sx={{ mt: 2 }}>
                  Ride Details
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={6}>
                    <Typography color="text.secondary">Distance</Typography>
                    <Typography variant="h6">
                      {(rideDetails.distance / 1000).toFixed(1)} km
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography color="text.secondary">Duration</Typography>
                    <Typography variant="h6">
                      {Math.round(rideDetails.duration / 60)} mins
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography color="text.secondary">Estimated Fare</Typography>
                    <Typography variant="h4" className="gradient-text">
                      Rs. {rideDetails.fare.toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            )}

            <Button
              variant="contained"
              fullWidth
              size="large"
              onClick={handleBookRide}
              disabled={loading || !rideDetails.pickup || !rideDetails.dropoff}
              sx={{
                mt: 3,
                py: 1.5,
                borderRadius: 2,
                background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
              }}
            >
              {loading ? <CircularProgress size={24} /> : 'Book Now'}
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <MapComponent
            customerLocation={rideDetails.pickup?.coordinates}
            route={rideDetails.route}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default RideBooking; 