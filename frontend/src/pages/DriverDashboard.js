import React from 'react';
import { Container, Grid, Paper, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const DriverDashboard = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Welcome Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h4" gutterBottom>
              Driver Dashboard
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Manage your rides, earnings, and schedule
            </Typography>
          </Paper>
        </Grid>

        {/* Current Ride */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Current Ride
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              View and manage your current ride details.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="contained"
                fullWidth
                onClick={() => navigate('/current-ride')}
              >
                View Details
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Earnings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Earnings
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Track your earnings and view payment history.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/driver-earnings')}
              >
                View Earnings
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Schedule */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Schedule
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Manage your working hours and availability.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/driver-schedule')}
              >
                Manage Schedule
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Ratings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Ratings & Reviews
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              View your ratings and customer feedback.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/driver-ratings')}
              >
                View Ratings
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DriverDashboard; 