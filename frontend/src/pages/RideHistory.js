import React from 'react';
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';

const RideHistory = () => {
  // Sample ride history data
  const rides = [
    {
      id: 1,
      date: '2024-03-15',
      pickup: '123 Main St',
      dropoff: '456 Market St',
      fare: '$25.00',
      status: 'Completed',
      driver: 'John Smith',
    },
    {
      id: 2,
      date: '2024-03-14',
      pickup: '789 Oak Ave',
      dropoff: '321 Pine St',
      fare: '$18.50',
      status: 'Completed',
      driver: 'Sarah Johnson',
    },
    // Add more sample rides
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
        return 'success';
      case 'Cancelled':
        return 'error';
      case 'In Progress':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Ride History
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Pickup</TableCell>
                <TableCell>Dropoff</TableCell>
                <TableCell>Driver</TableCell>
                <TableCell>Fare</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rides.map((ride) => (
                <TableRow key={ride.id}>
                  <TableCell>{ride.date}</TableCell>
                  <TableCell>{ride.pickup}</TableCell>
                  <TableCell>{ride.dropoff}</TableCell>
                  <TableCell>{ride.driver}</TableCell>
                  <TableCell>{ride.fare}</TableCell>
                  <TableCell>
                    <Chip
                      label={ride.status}
                      color={getStatusColor(ride.status)}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default RideHistory; 