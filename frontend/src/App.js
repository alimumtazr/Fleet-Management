import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useSelector } from 'react-redux';

// Import pages
import Login from './pages/Login';
import Register from './pages/Register';
import CustomerDashboard from './pages/CustomerDashboard';
import DriverDashboard from './pages/DriverDashboard';
import AdminDashboard from './pages/AdminDashboard';
import RideBooking from './pages/RideBooking';
import RideHistory from './pages/RideHistory';
import Payments from './pages/Payments';
import Profile from './pages/Profile';

// Create theme
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

const PrivateRoute = ({ children, roles }) => {
  const { user, isAuthenticated } = useSelector((state) => state.auth);

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/" />;
  }

  return children;
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Customer Routes */}
          <Route
            path="/dashboard"
            element={
              <PrivateRoute roles={['customer']}>
                <CustomerDashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/book-ride"
            element={
              <PrivateRoute roles={['customer']}>
                <RideBooking />
              </PrivateRoute>
            }
          />
          <Route
            path="/ride-history"
            element={
              <PrivateRoute roles={['customer']}>
                <RideHistory />
              </PrivateRoute>
            }
          />
          <Route
            path="/payments"
            element={
              <PrivateRoute roles={['customer']}>
                <Payments />
              </PrivateRoute>
            }
          />

          {/* Driver Routes */}
          <Route
            path="/driver-dashboard"
            element={
              <PrivateRoute roles={['driver']}>
                <DriverDashboard />
              </PrivateRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin-dashboard"
            element={
              <PrivateRoute roles={['admin']}>
                <AdminDashboard />
              </PrivateRoute>
            }
          />

          {/* Common Routes */}
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <Profile />
              </PrivateRoute>
            }
          />

          {/* Default Route */}
          <Route path="/" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 