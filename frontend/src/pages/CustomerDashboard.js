import React from 'react';
import { Container, Typography, Paper } from '@mui/material';

const CustomerDashboard = () => {
    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Paper sx={{ p: 3 }}>
                <Typography variant="h4" gutterBottom>
                    Customer Dashboard
                </Typography>
                <Typography variant="body1">
                    Welcome to your dashboard. Here you can manage your rides, view history, and update your profile.
                </Typography>
                {/* Add more dashboard components here */}
            </Paper>
        </Container>
    );
};

export default CustomerDashboard;