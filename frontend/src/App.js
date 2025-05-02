import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import Login from './pages/Login';
import Register from './pages/Register';
import RideBooking from './pages/RideBooking';
import DriverDashboard from './pages/DriverDashboard';
import authService from './services/authService';
import { WebSocketProvider } from './context/WebSocketContext';

const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
    },
});

const ProtectedRoute = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                // First check if we have a token
                if (!authService.isAuthenticated()) {
                    console.log('No token found, redirecting to login');
                    setIsAuthenticated(false);
                    setLoading(false);
                    return;
                }

                // Then try to get the current user
                const user = await authService.getCurrentUser();

                if (user) {
                    console.log('User authenticated:', user);
                    setIsAuthenticated(true);
                } else {
                    console.log('Failed to get user data, clearing token and redirecting to login');
                    // Clear the token if it's invalid
                    localStorage.removeItem('token');
                    setIsAuthenticated(false);
                }
            } catch (error) {
                console.error('Authentication error:', error);
                setError(error);
                setIsAuthenticated(false);
                // Clear the token on authentication errors
                localStorage.removeItem('token');
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, []);

    if (loading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                flexDirection: 'column'
            }}>
                <div style={{ marginBottom: '20px' }}>Loading...</div>
                <div>Verifying your authentication...</div>
            </div>
        );
    }

    if (error) {
        return <Navigate to="/login?error=true" />;
    }

    return isAuthenticated ? children : <Navigate to="/login" />;
};

const App = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <WebSocketProvider>
                <Router>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route
                            path="/"
                            element={
                                <ProtectedRoute>
                                    <RideBooking />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/driver-dashboard"
                            element={
                                <ProtectedRoute>
                                    <DriverDashboard />
                                </ProtectedRoute>
                            }
                        />
                    </Routes>
                </Router>
            </WebSocketProvider>
        </ThemeProvider>
    );
};

export default App;