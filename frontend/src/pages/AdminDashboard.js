import React, { useState } from 'react';
import { Grid, Paper, Typography, Button, Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import MainLayout from '../components/layout/MainLayout';
import { useNavigate } from 'react-router-dom';
import PeopleIcon from '@mui/icons-material/People';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [recentDrivers, setRecentDrivers] = useState([
    {
      id: 1,
      name: 'John Smith',
      vehicle: 'Toyota Camry',
      status: 'Active',
      rating: 4.8
    },
    // Add more sample drivers
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
              startIcon={<PeopleIcon />}
              onClick={() => navigate('/drivers')}
            >
              Manage Drivers
            </Button>
            <Button
              variant="outlined"
              startIcon={<PeopleIcon />}
              onClick={() => navigate('/customers')}
            >
              Manage Customers
            </Button>
            <Button
              variant="outlined"
              startIcon={<DirectionsCarIcon />}
              onClick={() => navigate('/rides')}
            >
              View All Rides
            </Button>
          </Paper>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Total Drivers
            </Typography>
            <Typography variant="h4">45</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Total Customers
            </Typography>
            <Typography variant="h4">1200</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Total Rides
            </Typography>
            <Typography variant="h4">3500</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Revenue
            </Typography>
            <Typography variant="h4">$25,000</Typography>
          </Paper>
        </Grid>

        {/* Recent Drivers */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Recent Drivers
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Vehicle</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Rating</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentDrivers.map((driver) => (
                  <TableRow key={driver.id}>
                    <TableCell>{driver.id}</TableCell>
                    <TableCell>{driver.name}</TableCell>
                    <TableCell>{driver.vehicle}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        size="small"
                        color={driver.status === 'Active' ? 'success' : 'error'}
                      >
                        {driver.status}
                      </Button>
                    </TableCell>
                    <TableCell>{driver.rating}/5</TableCell>
                    <TableCell>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => navigate(`/drivers/${driver.id}`)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>

        {/* Revenue Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Revenue Overview
            </Typography>
            <Button
              variant="outlined"
              startIcon={<TrendingUpIcon />}
              onClick={() => navigate('/revenue')}
            >
              View Detailed Report
            </Button>
            {/* Add chart component here */}
          </Paper>
        </Grid>
      </Grid>
    </MainLayout>
  );
};

export default AdminDashboard; 