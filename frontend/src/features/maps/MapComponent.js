import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Box, Paper, Typography } from '@mui/material';
import { useSelector } from 'react-redux';

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom marker icons
const driverIcon = new L.Icon({
  iconUrl: '/assets/driver-marker.png',
  iconSize: [35, 35],
  iconAnchor: [17, 35],
  popupAnchor: [0, -35],
});

const customerIcon = new L.Icon({
  iconUrl: '/assets/customer-marker.png',
  iconSize: [35, 35],
  iconAnchor: [17, 35],
  popupAnchor: [0, -35],
});

// Component to update map center
const MapUpdater = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
};

const MapComponent = ({
  center = [31.5204, 74.3587], // Default center (Lahore)
  driverLocation,
  customerLocation,
  route,
  geofence,
}) => {
  const [mapCenter, setMapCenter] = useState(center);
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    if (driverLocation && customerLocation) {
      // Calculate bounds to fit both markers
      const bounds = L.latLngBounds([driverLocation, customerLocation]);
      setMapCenter(bounds.getCenter());
    } else if (driverLocation) {
      setMapCenter(driverLocation);
    } else if (customerLocation) {
      setMapCenter(customerLocation);
    }
  }, [driverLocation, customerLocation]);

  return (
    <Paper elevation={3} sx={{ height: '500px', width: '100%', borderRadius: 2 }}>
      <MapContainer
        center={mapCenter}
        zoom={13}
        style={{ height: '100%', width: '100%', borderRadius: 'inherit' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapUpdater center={mapCenter} />

        {driverLocation && (
          <Marker position={driverLocation} icon={driverIcon}>
            <Popup>
              <Typography variant="body2">Driver's Location</Typography>
            </Popup>
          </Marker>
        )}

        {customerLocation && (
          <Marker position={customerLocation} icon={customerIcon}>
            <Popup>
              <Typography variant="body2">Customer's Location</Typography>
            </Popup>
          </Marker>
        )}

        {route && (
          <Polyline
            positions={route}
            color="#2196f3"
            weight={4}
            opacity={0.7}
            dashArray="10, 10"
          />
        )}

        {geofence && (
          <Circle
            center={center}
            radius={geofence.radius}
            pathOptions={{ color: '#f50057', fillColor: '#f50057', fillOpacity: 0.1 }}
          />
        )}
      </MapContainer>
    </Paper>
  );
};

export default MapComponent; 