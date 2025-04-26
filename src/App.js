import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import RideBooking from './pages/RideBooking';
import DriverDashboard from './pages/DriverDashboard';
import Profile from './pages/Profile';
import RideHistory from './pages/RideHistory';
import { WebSocketProvider } from './context/WebSocketContext';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <WebSocketProvider>
        <Router>
          <div className="app">
            <Navbar />
            <main className="main-content">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/book-ride" element={<RideBooking />} />
                <Route path="/driver-dashboard" element={<DriverDashboard />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/ride-history" element={<RideHistory />} />
              </Routes>
            </main>
          </div>
        </Router>
      </WebSocketProvider>
    </ThemeProvider>
  );
}

export default App; 