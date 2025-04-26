import axios from 'axios';

const OPENROUTE_API_KEY = '5b3ce3597851110001cf62481035bf7b464646dfa63334a3ace37eb5';
const OPENROUTE_BASE_URL = 'https://api.openrouteservice.org/v2';

export const mapService = {
    // Get directions between two points
    getDirections: async (start, end) => {
        try {
            const response = await axios.get(`${OPENROUTE_BASE_URL}/directions/driving-car`, {
                params: {
                    api_key: OPENROUTE_API_KEY,
                    start: `${start.lng},${start.lat}`,
                    end: `${end.lng},${end.lat}`
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error getting directions:', error);
            throw error;
        }
    },

    // Get geocoding (address to coordinates)
    geocode: async (address) => {
        try {
            const response = await axios.get(`${OPENROUTE_BASE_URL}/geocode/search`, {
                params: {
                    api_key: OPENROUTE_API_KEY,
                    text: address
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error geocoding address:', error);
            throw error;
        }
    },

    // Get reverse geocoding (coordinates to address)
    reverseGeocode: async (lat, lng) => {
        try {
            const response = await axios.get(`${OPENROUTE_BASE_URL}/geocode/reverse`, {
                params: {
                    api_key: OPENROUTE_API_KEY,
                    point: `${lng},${lat}`
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error reverse geocoding:', error);
            throw error;
        }
    },

    // Get isochrones (reachable areas)
    getIsochrones: async (location, range) => {
        try {
            const response = await axios.get(`${OPENROUTE_BASE_URL}/isochrones/driving-car`, {
                params: {
                    api_key: OPENROUTE_API_KEY,
                    locations: `${location.lng},${location.lat}`,
                    range: range
                }
            });
            return response.data;
        } catch (error) {
            console.error('Error getting isochrones:', error);
            throw error;
        }
    }
}; 