import React from 'react';
import { Container, Grid, Paper, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const CustomerDashboard = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Welcome Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h4" gutterBottom>
              Welcome to Fleet Management System
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Book your ride, track your trips, and manage your payments
            </Typography>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Book a Ride
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Need to go somewhere? Book a ride with our professional drivers.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="contained"
                fullWidth
                onClick={() => navigate('/book-ride')}
              >
                Book Now
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Ride History */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Ride History
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              View your past rides and track your journey history.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/ride-history')}
              >
                View History
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Payments */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Payments
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Manage your payment methods and view transaction history.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/payments')}
              >
                Manage Payments
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CustomerDashboard; 