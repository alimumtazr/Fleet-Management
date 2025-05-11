import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { createTheme } from '@mui/material/styles';
import { useDispatch } from 'react-redux';
import { login } from './store/slices/authSlice';
import Login from './pages/Login';
import Register from './pages/Register';
import RideBooking from './pages/RideBooking';
import DriverDashboard from './pages/DriverDashboard';
import CustomerDashboard from './pages/CustomerDashboard';
import RideHistory from './pages/RideHistory';
import Profile from './pages/Profile';
import Payments from './pages/Payments';
import AdminDashboard from './pages/AdminDashboard';
import authService from './services/authService';
import { WebSocketProvider } from './context/WebSocketContext';
import MainLayout from './components/layout/MainLayout';

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
    <div style={{ 
        padding: '30px', 
        maxWidth: '1200px', 
        margin: '0 auto',
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 3px 10px rgba(0,0,0,0.08)'
    }}>
        <h2 style={{ 
            color: '#1976d2', 
            marginBottom: '16px',
            fontWeight: 500
        }}>{title}</h2>
        <p style={{ color: '#666', fontSize: '16px' }}>
            This page is currently under development. Check back soon for new features and functionality.
        </p>
        <div style={{ 
            marginTop: '20px', 
            padding: '15px', 
            backgroundColor: '#f5f9ff', 
            borderLeft: '4px solid #1976d2',
            borderRadius: '4px'
        }}>
            <p style={{ margin: 0, color: '#444' }}>
                We're constantly improving our Fleet Management System to provide you with the best experience.
            </p>
        </div>
    </div>
);

const App = () => {
    const dispatch = useDispatch();
    
    // On app load, check for saved user state and restore it
    useEffect(() => {
        const restoreUserSession = async () => {
            try {
                if (authService.isAuthenticated()) {
                    console.log('[App] Found authentication token, fetching user data...');
                    const userData = await authService.getCurrentUser();
                    if (userData && userData.user) {
                        console.log('[App] Restoring user session:', userData.user);
                        dispatch(login(userData.user));
                    } else {
                        console.log('[App] No valid user data found, clearing token');
                        authService.logout();
                    }
                } else {
                    console.log('[App] No authentication token found');
                }
            } catch (error) {
                console.error('[App] Error restoring user session:', error);
                authService.logout();
            }
        };
        
        restoreUserSession();
    }, [dispatch]);
    
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
                            element={<ProtectedRoute><MainLayout><RideBooking /></MainLayout></ProtectedRoute>}
                        />
                        <Route
                            path="/customer-dashboard"
                            element={<ProtectedRoute><MainLayout><CustomerDashboard /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/ride-history"
                            element={<ProtectedRoute><MainLayout><RideHistory /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/profile"
                            element={<ProtectedRoute><MainLayout><Profile /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/payments"
                            element={<ProtectedRoute><MainLayout><Payments /></MainLayout></ProtectedRoute>}
                        />

                        {/* Driver Routes */}
                        <Route
                            path="/driver-dashboard"
                            element={<ProtectedRoute><MainLayout><DriverDashboard /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/current-ride"
                            element={<ProtectedRoute><MainLayout><PlaceholderComponent title="Current Ride Details" /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/driver-earnings"
                            element={<ProtectedRoute><MainLayout><PlaceholderComponent title="Driver Earnings" /></MainLayout></ProtectedRoute>}
                        />
                        
                        {/* Admin Routes */}
                        <Route
                            path="/admin-dashboard"
                            element={<ProtectedRoute><MainLayout><AdminDashboard /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/drivers"
                            element={<ProtectedRoute><MainLayout><PlaceholderComponent title="Manage Drivers" /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/customers"
                            element={<ProtectedRoute><MainLayout><PlaceholderComponent title="Manage Customers" /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/rides"
                            element={<ProtectedRoute><MainLayout><PlaceholderComponent title="Manage Rides" /></MainLayout></ProtectedRoute>}
                        />
                        <Route 
                            path="/settings"
                            element={<ProtectedRoute><MainLayout><PlaceholderComponent title="System Settings" /></MainLayout></ProtectedRoute>}
                        />

                        {/* Fallback for unknown routes - redirect to dashboard */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </Router>
            </WebSocketProvider>
        </ThemeProvider>
    );
};

export default App;