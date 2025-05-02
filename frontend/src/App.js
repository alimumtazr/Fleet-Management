import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import Login from './pages/Login';
import Register from './pages/Register';
import RideBooking from './pages/RideBooking';
import DriverDashboard from './pages/DriverDashboard';
import CustomerDashboard from './pages/CustomerDashboard'; // Import CustomerDashboard
import RideHistory from './pages/RideHistory'; // Import placeholder
import Profile from './pages/Profile'; // Import placeholder
import Payments from './pages/Payments'; // Import placeholder
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
    const [isAuthenticated, setIsAuthenticated] = useState(null); // Initialize as null
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        console.log('[ProtectedRoute] Checking auth...');
        const checkAuth = async () => {
            setLoading(true); // Ensure loading is true at the start
            setError(null);
            try {
                const hasToken = authService.isAuthenticated();
                console.log(`[ProtectedRoute] Token exists: ${hasToken}`);
                if (!hasToken) {
                    console.log('[ProtectedRoute] No token, setting auth false.');
                    setIsAuthenticated(false);
                    setLoading(false);
                    return;
                }

                console.log('[ProtectedRoute] Token found, attempting to get user...');
                const user = await authService.getCurrentUser();

                if (user) {
                    console.log('[ProtectedRoute] User fetched successfully:', user);
                    setIsAuthenticated(true);
                } else {
                    console.log('[ProtectedRoute] Failed to get user data (token might be invalid/expired).');
                    localStorage.removeItem('token'); // Clear invalid token
                    setIsAuthenticated(false);
                }
            } catch (err) {
                console.error('[ProtectedRoute] Authentication error:', err);
                setError(err);
                setIsAuthenticated(false);
                localStorage.removeItem('token'); // Clear token on error
            } finally {
                console.log('[ProtectedRoute] Auth check finished.');
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

    // Handle case where isAuthenticated is still null (shouldn't happen often)
    if (isAuthenticated === null) {
         console.log('[ProtectedRoute] Auth state still null after loading, showing loading...');
         return <div>Verifying authentication...</div>; // Or a more robust loading indicator
    }

    if (error) {
        console.log('[ProtectedRoute] Auth error, redirecting to login.');
        return <Navigate to="/login?error=true" replace />;
    }

    console.log(`[ProtectedRoute] Rendering children: ${isAuthenticated}`);
    return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Simple placeholder component
const PlaceholderComponent = ({ title }) => (
    <div style={{ padding: '20px' }}>
        <h2>{title}</h2>
        <p>This page is under construction.</p>
    </div>
);

const App = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <WebSocketProvider>
                <Router>
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        
                        {/* Customer Routes */}
                        <Route
                            path="/"
                            element={<ProtectedRoute><RideBooking /></ProtectedRoute>}
                        />
                        <Route
                            path="/customer-dashboard"
                            element={<ProtectedRoute><CustomerDashboard /></ProtectedRoute>}
                        />
                        <Route 
                            path="/ride-history"
                            element={<ProtectedRoute><RideHistory /></ProtectedRoute>}
                        />
                        <Route 
                            path="/profile"
                            element={<ProtectedRoute><Profile /></ProtectedRoute>}
                        />
                        <Route 
                            path="/payments"
                            element={<ProtectedRoute><Payments /></ProtectedRoute>}
                        />

                        {/* Driver Routes */}
                        <Route
                            path="/driver-dashboard"
                            element={<ProtectedRoute><DriverDashboard /></ProtectedRoute>}
                        />
                        {/* Add placeholder routes for driver dashboard links */}
                        <Route 
                            path="/current-ride"
                            element={<ProtectedRoute><PlaceholderComponent title="Current Ride Details" /></ProtectedRoute>}
                        />
                        <Route 
                            path="/driver-earnings"
                            element={<ProtectedRoute><PlaceholderComponent title="Driver Earnings" /></ProtectedRoute>}
                        />
                        <Route 
                            path="/driver-schedule"
                            element={<ProtectedRoute><PlaceholderComponent title="Driver Schedule" /></ProtectedRoute>}
                        />
                        <Route 
                            path="/driver-ratings"
                            element={<ProtectedRoute><PlaceholderComponent title="Driver Ratings" /></ProtectedRoute>}
                        />

                        {/* Fallback for unknown routes - maybe redirect to dashboard or 404 */}
                        <Route path="*" element={<Navigate to="/" replace />} />

                    </Routes>
                </Router>
            </WebSocketProvider>
        </ThemeProvider>
    );
};

export default App;