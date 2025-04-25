import React, { useState } from 'react';
import { Grid, Paper, Typography, Button, Card, CardContent } from '@mui/material';
import MainLayout from '../components/layout/MainLayout';
import { useNavigate } from 'react-router-dom';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PaymentIcon from '@mui/icons-material/Payment';

const CustomerDashboard = () => {
  const navigate = useNavigate();
  const [recentRides, setRecentRides] = useState([
    {
      id: 1,
      pickup: '123 Main St',
      dropoff: '456 Market St',
      date: '2024-03-15',
      fare: '$25.00',
      status: 'Completed'
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
              startIcon={<LocationOnIcon />}
              onClick={() => navigate('/book-ride')}
            >
              Book a Ride
            </Button>
            <Button
              variant="outlined"
              startIcon={<AccessTimeIcon />}
              onClick={() => navigate('/ride-history')}
            >
              View History
            </Button>
            <Button
              variant="outlined"
              startIcon={<PaymentIcon />}
              onClick={() => navigate('/payments')}
            >
              Payment Methods
            </Button>
          </Paper>
        </Grid>

        {/* Recent Rides */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Recent Rides
          </Typography>
          <Grid container spacing={2}>
            {recentRides.map((ride) => (
              <Grid item xs={12} sm={6} md={4} key={ride.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Ride #{ride.id}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      From: {ride.pickup}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      To: {ride.dropoff}
                    </Typography>
                    <Typography color="textSecondary" gutterBottom>
                      Date: {ride.date}
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {ride.fare}
                    </Typography>
                    <Typography
                      color={ride.status === 'Completed' ? 'success.main' : 'warning.main'}
                    >
                      {ride.status}
                    </Typography>
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
              Total Rides
            </Typography>
            <Typography variant="h4">12</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Total Spent
            </Typography>
            <Typography variant="h4">$250.00</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Average Rating
            </Typography>
            <Typography variant="h4">4.8/5</Typography>
          </Paper>
        </Grid>
      </Grid>
    </MainLayout>
  );
};

export default CustomerDashboard; 