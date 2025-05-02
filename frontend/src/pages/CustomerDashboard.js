import React from 'react';
import { Container, Grid, Paper, Typography, Button, Box, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import HistoryIcon from '@mui/icons-material/History';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import PaymentIcon from '@mui/icons-material/Payment';
import LogoutIcon from '@mui/icons-material/Logout';
import authService from '../services/authService'; // Import authService

const CustomerDashboard = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        authService.logout();
        navigate('/login');
    };

    const menuItems = [
        { text: 'Book a Ride', icon: <DirectionsCarIcon />, path: '/' },
        { text: 'Ride History', icon: <HistoryIcon />, path: '/ride-history' },
        { text: 'Profile', icon: <AccountCircleIcon />, path: '/profile' },
        { text: 'Payments', icon: <PaymentIcon />, path: '/payments' },
    ];

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Grid container spacing={3}>
                {/* Sidebar Navigation */}
                <Grid item xs={12} md={3}>
                    <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
                        <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
                            Menu
                        </Typography>
                        <List component="nav">
                            {menuItems.map((item) => (
                                <ListItem button key={item.text} onClick={() => navigate(item.path)}>
                                    <ListItemIcon>{item.icon}</ListItemIcon>
                                    <ListItemText primary={item.text} />
                                </ListItem>
                            ))}
                        </List>
                        <Box sx={{ mt: 'auto' }}>
                            <ListItem button onClick={handleLogout}>
                                <ListItemIcon><LogoutIcon /></ListItemIcon>
                                <ListItemText primary="Logout" />
                            </ListItem>
                        </Box>
                    </Paper>
                </Grid>

                {/* Main Content Area */}
                <Grid item xs={12} md={9}>
                    <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column' }}>
                        <Typography variant="h4" gutterBottom>
                            Welcome, Customer!
                        </Typography>
                        <Typography variant="body1" color="text.secondary" paragraph>
                            Manage your rides and account details here.
                        </Typography>
                        
                        {/* Quick Actions or Summary */}
                        <Grid container spacing={2} sx={{ mt: 2 }}>
                            <Grid item xs={12} sm={6}>
                                <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
                                    <Typography variant="h6">Ready to Go?</Typography>
                                    <Button 
                                        variant="contained" 
                                        startIcon={<DirectionsCarIcon />} 
                                        sx={{ mt: 2 }}
                                        onClick={() => navigate('/')}
                                    >
                                        Book a New Ride
                                    </Button>
                                </Paper>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
                                    <Typography variant="h6">Recent Activity</Typography>
                                    <Button 
                                        variant="outlined" 
                                        startIcon={<HistoryIcon />} 
                                        sx={{ mt: 2 }}
                                        onClick={() => navigate('/ride-history')}
                                    >
                                        View Ride History
                                    </Button>
                                </Paper>
                            </Grid>
                        </Grid>
                        {/* Add more dashboard widgets or content here */}
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    );
};

export default CustomerDashboard;