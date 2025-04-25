import React from 'react';
import { Container, Grid, Paper, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Welcome Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h4" gutterBottom>
              Admin Dashboard
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Manage your fleet, drivers, and system settings
            </Typography>
          </Paper>
        </Grid>

        {/* Fleet Management */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Fleet Management
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Manage vehicles, maintenance, and fleet operations.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="contained"
                fullWidth
                onClick={() => navigate('/fleet-management')}
              >
                Manage Fleet
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Driver Management */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Driver Management
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Manage drivers, their documents, and performance.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/driver-management')}
              >
                Manage Drivers
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Analytics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Analytics
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              View system analytics and generate reports.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/analytics')}
              >
                View Analytics
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* System Settings */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              System Settings
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Configure system settings and manage users.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/system-settings')}
              >
                Manage Settings
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Customer Support */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Customer Support
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Manage customer support tickets and queries.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/customer-support')}
              >
                View Support
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Payment Management */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 200 }}>
            <Typography variant="h6" gutterBottom>
              Payment Management
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Manage payments, invoices, and financial records.
            </Typography>
            <Box sx={{ mt: 'auto' }}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => navigate('/payment-management')}
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

export default AdminDashboard; 