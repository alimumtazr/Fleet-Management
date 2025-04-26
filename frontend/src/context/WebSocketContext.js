import React, { createContext, useContext, useEffect, useState } from 'react';
import authService from '../services/authService';

const WebSocketContext = createContext(null);

export const useWebSocket = () => {
    const context = useContext(WebSocketContext);
    if (!context) {
        throw new Error('useWebSocket must be used within a WebSocketProvider');
    }
    return context;
};

export const WebSocketProvider = ({ children }) => {
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        const connectWebSocket = async () => {
            try {
                const user = await authService.getCurrentUser();
                if (!user) return;

                const ws = new WebSocket(`ws://localhost:8000/ws/${user.id}`);
                
                ws.onopen = () => {
                    console.log('WebSocket Connected');
                    setIsConnected(true);
                };

                ws.onclose = () => {
                    console.log('WebSocket Disconnected');
                    setIsConnected(false);
                };

                ws.onerror = (error) => {
                    console.error('WebSocket Error:', error);
                    setIsConnected(false);
                };

                setSocket(ws);

                return () => {
                    ws.close();
                };
            } catch (error) {
                console.error('Error connecting to WebSocket:', error);
            }
        };

        connectWebSocket();
    }, []);

    const value = {
        socket,
        isConnected,
    };

    return (
        <WebSocketContext.Provider value={value}>
            {children}
        </WebSocketContext.Provider>
    );
}; 