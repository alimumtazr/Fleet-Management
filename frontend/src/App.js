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

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const user = await authService.getCurrentUser();
                setIsAuthenticated(!!user);
            } catch (error) {
                setIsAuthenticated(false);
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, []);

    if (loading) {
        return <div>Loading...</div>;
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