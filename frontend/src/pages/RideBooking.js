import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Icon } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { mapService } from '../services/mapService';
import { Box, TextField, Button, Typography, Paper, CircularProgress, Autocomplete } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useWebSocket } from '../context/WebSocketContext';

// Fix for default marker icons
delete Icon.Default.prototype._getIconUrl;
Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const StyledMapContainer = styled(MapContainer)({
    height: '100%',
    width: '100%',
    zIndex: 1,
});

const BookingContainer = styled(Paper)(({ theme }) => ({
    position: 'absolute',
    top: theme.spacing(2),
    left: theme.spacing(2),
    padding: theme.spacing(3),
    maxWidth: 400,
    width: '90%',
    zIndex: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(10px)',
}));

const RideBooking = () => {
    const [pickup, setPickup] = useState(null);
    const [destination, setDestination] = useState(null);
    const [route, setRoute] = useState(null);
    const [nearbyDrivers, setNearbyDrivers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [suggestions, setSuggestions] = useState([]);
    const { socket, isConnected } = useWebSocket();
    const mapRef = useRef();

    useEffect(() => {
        if (socket && isConnected) {
            socket.on('driverUpdate', (data) => {
                setNearbyDrivers(data.drivers);
            });
        }
    }, [socket, isConnected]);

    const handleSearch = async (value, type) => {
        if (!value) return;
        try {
            const response = await mapService.geocode(value);
            const features = response.features.map(feature => ({
                label: feature.properties.label,
                coordinates: feature.geometry.coordinates,
            }));
            setSuggestions(features);
        } catch (error) {
            console.error('Error searching location:', error);
        }
    };

    const handleLocationSelect = (option, type) => {
        const location = {
            lat: option.coordinates[1],
            lng: option.coordinates[0],
            address: option.label
        };
        if (type === 'pickup') {
            setPickup(location);
        } else {
            setDestination(location);
        }
    };

    const calculateRoute = async () => {
        if (!pickup || !destination) return;
        setLoading(true);
        try {
            const routeData = await mapService.getDirections(pickup, destination);
            setRoute(routeData);
            
            // Notify nearby drivers about the ride request
            if (socket && isConnected) {
                socket.emit('rideRequest', {
                    pickup,
                    destination,
                    route: routeData
                });
            }
        } catch (error) {
            console.error('Error calculating route:', error);
        }
        setLoading(false);
    };

    return (
        <Box sx={{ height: '100vh', position: 'relative' }}>
            <StyledMapContainer
                center={[31.5204, 74.3587]} // Default to Lahore coordinates
                zoom={13}
                ref={mapRef}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                
                {pickup && (
                    <Marker position={[pickup.lat, pickup.lng]}>
                        <Popup>Pickup Location</Popup>
                    </Marker>
                )}
                
                {destination && (
                    <Marker position={[destination.lat, destination.lng]}>
                        <Popup>Destination</Popup>
                    </Marker>
                )}
                
                {nearbyDrivers.map((driver, index) => (
                    <Marker
                        key={index}
                        position={[driver.lat, driver.lng]}
                        icon={new Icon({
                            iconUrl: '/driver-marker.png',
                            iconSize: [32, 32],
                        })}
                    >
                        <Popup>Driver {driver.id}</Popup>
                    </Marker>
                ))}
            </StyledMapContainer>

            <BookingContainer elevation={3}>
                <Typography variant="h5" gutterBottom>
                    Book a Ride
                </Typography>
                
                <Autocomplete
                    options={suggestions}
                    getOptionLabel={(option) => option.label}
                    onChange={(event, newValue) => handleLocationSelect(newValue, 'pickup')}
                    onInputChange={(event, newInputValue) => handleSearch(newInputValue, 'pickup')}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label="Pickup Location"
                            fullWidth
                            margin="normal"
                        />
                    )}
                />
                
                <Autocomplete
                    options={suggestions}
                    getOptionLabel={(option) => option.label}
                    onChange={(event, newValue) => handleLocationSelect(newValue, 'destination')}
                    onInputChange={(event, newInputValue) => handleSearch(newInputValue, 'destination')}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label="Destination"
                            fullWidth
                            margin="normal"
                        />
                    )}
                />
                
                <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={calculateRoute}
                    disabled={!pickup || !destination || loading}
                    sx={{ mt: 2 }}
                >
                    {loading ? <CircularProgress size={24} /> : 'Find Ride'}
                </Button>
                
                {route && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle1">
                            Estimated Distance: {(route.routes[0].summary.distance / 1000).toFixed(1)} km
                        </Typography>
                        <Typography variant="subtitle1">
                            Estimated Duration: {Math.round(route.routes[0].summary.duration / 60)} minutes
                        </Typography>
                    </Box>
                )}
            </BookingContainer>
        </Box>
    );
};

export default RideBooking; 