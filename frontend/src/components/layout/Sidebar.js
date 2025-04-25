import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import PeopleIcon from '@mui/icons-material/People';
import HistoryIcon from '@mui/icons-material/History';
import SettingsIcon from '@mui/icons-material/Settings';
import PaymentIcon from '@mui/icons-material/Payment';

const drawerWidth = 240;

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useSelector((state) => state.auth);

  const customerMenuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Book Ride', icon: <DirectionsCarIcon />, path: '/book-ride' },
    { text: 'Ride History', icon: <HistoryIcon />, path: '/ride-history' },
    { text: 'Payments', icon: <PaymentIcon />, path: '/payments' },
  ];

  const driverMenuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/driver-dashboard' },
    { text: 'Active Rides', icon: <DirectionsCarIcon />, path: '/active-rides' },
    { text: 'Ride History', icon: <HistoryIcon />, path: '/ride-history' },
    { text: 'Earnings', icon: <PaymentIcon />, path: '/earnings' },
  ];

  const adminMenuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin-dashboard' },
    { text: 'Drivers', icon: <PeopleIcon />, path: '/drivers' },
    { text: 'Customers', icon: <PeopleIcon />, path: '/customers' },
    { text: 'Rides', icon: <DirectionsCarIcon />, path: '/rides' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  const menuItems = user?.role === 'admin' 
    ? adminMenuItems 
    : user?.role === 'driver' 
      ? driverMenuItems 
      : customerMenuItems;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar />
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => navigate(item.path)}
            selected={location.pathname === item.path}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar; 