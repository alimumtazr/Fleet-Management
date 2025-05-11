import React, { useState, useEffect } from 'react';
import { 
  Tabs, 
  Tab, 
  Box, 
  useMediaQuery, 
  useTheme,
  Badge,
  Typography
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

// Icons
import HomeIcon from '@mui/icons-material/Home';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';
import HistoryIcon from '@mui/icons-material/History';
import PaymentIcon from '@mui/icons-material/Payment';
import PersonIcon from '@mui/icons-material/Person';
import PeopleIcon from '@mui/icons-material/People';
import SettingsIcon from '@mui/icons-material/Settings';
import DashboardIcon from '@mui/icons-material/Dashboard';

const TabNavigation = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const [value, setValue] = useState(0);

  // Debug logging
  console.log('TabNavigation - User:', user);
  console.log('TabNavigation - User type:', user?.user_type);
  console.log('TabNavigation - isAuthenticated:', isAuthenticated);

  // Define navigation items based on user role
  const customerTabs = [
    { label: 'Dashboard', icon: <HomeIcon />, path: '/customer-dashboard' },
    { label: 'Book Ride', icon: <DirectionsCarIcon />, path: '/' },
    { label: 'History', icon: <HistoryIcon />, path: '/ride-history' },
    { label: 'Payments', icon: <PaymentIcon />, path: '/payments' },
    { label: 'Profile', icon: <PersonIcon />, path: '/profile' },
  ];

  const driverTabs = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/driver-dashboard' },
    { label: 'Current Ride', icon: <DirectionsCarIcon />, path: '/current-ride' },
    { label: 'History', icon: <HistoryIcon />, path: '/ride-history' },
    { label: 'Earnings', icon: <PaymentIcon />, path: '/driver-earnings' },
    { label: 'Profile', icon: <PersonIcon />, path: '/profile' },
  ];

  const adminTabs = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/admin-dashboard' },
    { label: 'Drivers', icon: <PeopleIcon />, path: '/drivers' },
    { label: 'Customers', icon: <PeopleIcon />, path: '/customers' },
    { label: 'Rides', icon: <DirectionsCarIcon />, path: '/rides' },
    { label: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  // Determine which tabs to show based on user role
  const tabs = user?.user_type === 'admin' 
    ? adminTabs 
    : user?.user_type === 'driver' 
      ? driverTabs 
      : customerTabs;

  // Update the tab value when location changes
  useEffect(() => {
    const currentTab = tabs.findIndex(tab => tab.path === location.pathname);
    if (currentTab !== -1) {
      setValue(currentTab);
    }
  }, [location.pathname, tabs]);

  const handleChange = (event, newValue) => {
    setValue(newValue);
    navigate(tabs[newValue].path);
  };

  return (
    <Box 
      sx={{ 
        width: '100%', 
        bgcolor: 'background.paper',
        boxShadow: '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
        position: 'sticky',
        top: 64, // Below the AppBar
        zIndex: theme.zIndex.appBar - 1,
      }}
    >
      <Tabs
        value={value}
        onChange={handleChange}
        variant={isTablet ? "scrollable" : "fullWidth"}
        scrollButtons={isTablet ? "auto" : false}
        allowScrollButtonsMobile
        textColor="primary"
        indicatorColor="primary"
        aria-label="navigation tabs"
        sx={{
          '& .MuiTab-root': {
            minHeight: 64,
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              backgroundColor: 'rgba(25, 118, 210, 0.04)',
            },
          },
          '& .Mui-selected': {
            color: theme.palette.primary.main,
            fontWeight: 'bold',
          },
        }}
      >
        {tabs.map((tab, index) => (
          <Tab 
            key={index}
            icon={
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                {tab.icon}
                {!isMobile && (
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      mt: 0.5, 
                      fontSize: '0.7rem',
                      fontWeight: value === index ? 'bold' : 'normal',
                      textTransform: 'none'
                    }}
                  >
                    {tab.label}
                  </Typography>
                )}
              </Box>
            }
            aria-label={tab.label}
            sx={{ 
              minWidth: isTablet ? 70 : 120,
              py: 1.5,
              px: 2,
            }}
          />
        ))}
      </Tabs>
    </Box>
  );
};

export default TabNavigation; 