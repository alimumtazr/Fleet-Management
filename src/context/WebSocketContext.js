import React, { createContext, useContext, useEffect, useState } from 'react';

const WebSocketContext = createContext();

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [nearbyDrivers, setNearbyDrivers] = useState([]);
  const [currentRide, setCurrentRide] = useState(null);

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (!userId) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

    ws.onopen = () => {
      console.log('WebSocket Connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'nearby_drivers':
          setNearbyDrivers(data.data);
          break;
        case 'ride_accepted':
        case 'ride_started':
        case 'ride_completed':
          setCurrentRide(prev => ({
            ...prev,
            ...data.data,
            status: data.type
          }));
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket Disconnected');
      setIsConnected(false);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  const updateLocation = (location) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify({
        type: 'location_update',
        location
      }));
    }
  };

  const subscribeToRide = (rideId) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify({
        type: 'subscribe_ride',
        ride_id: rideId
      }));
    }
  };

  const value = {
    socket,
    isConnected,
    nearbyDrivers,
    currentRide,
    updateLocation,
    subscribeToRide
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}; 