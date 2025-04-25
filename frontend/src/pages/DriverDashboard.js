import React, { useState } from 'react';
import { Grid, Paper, Typography, Button, Card, CardContent, Chip } from '@mui/material';
import MainLayout from '../components/layout/MainLayout';
import { useNavigate } from 'react-router-dom';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import PaymentIcon from '@mui/icons-material/Payment';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

const DriverDashboard = () => {
  const navigate = useNavigate();
  const [activeRides, setActiveRides] = useState([
    {
      id: 1,
      passenger: 'John Doe',
      pickup: '123 Main St',
      dropoff: '456 Market St',
      fare: '$25.00',
      status: 'In Progress'
    },
    // Add more sample rides
  ]);

  return (
    <MainLayout>
      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<DirectionsCarIcon />}
              onClick={() => navigate('/active-rides')}
            >
              View Active Rides
            </Button>
            <Button
              variant="outlined"
              startIcon={<PaymentIcon />}
              onClick={() => navigate('/earnings')}
            >
              View Earnings
            </Button>
            <Button
              variant="outlined"
              startIcon={<AccessTimeIcon />}
              onClick={() => navigate('/ride-history')}
            >
              Ride History
            </Button>
          </Paper>
        </Grid>

        {/* Active Rides */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Active Rides
          </Typography>
          <Grid container spacing={2}>
            {activeRides.map((ride) => (
              <Grid item xs={12} sm={6} md={4} key={ride.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Ride #{ride.id}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      Passenger: {ride.passenger}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      From: {ride.pickup}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      To: {ride.dropoff}
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {ride.fare}
                    </Typography>
                    <Chip
                      label={ride.status}
                      color={ride.status === 'In Progress' ? 'primary' : 'default'}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Today's Earnings
            </Typography>
            <Typography variant="h4">$150.00</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Total Rides
            </Typography>
            <Typography variant="h4">45</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Rating
            </Typography>
            <Typography variant="h4">4.9/5</Typography>
          </Paper>
        </Grid>
      </Grid>
    </MainLayout>
  );
};

export default DriverDashboard; 