import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Add a request interceptor to automatically add the token to all requests
axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('Added token to request:', config.url);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

const authService = {
    login: async (email, password) => {
        try {
            console.log('Attempting login with:', { email, password });
            console.log('API URL:', `${API_URL}/api/auth/login`);

            const response = await axios.post(`${API_URL}/api/auth/login`, {
                email,
                password
            });

            console.log('Login response:', response.data);

            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                console.log('Token saved to localStorage');
            }

            return response.data;
        } catch (error) {
            console.error('Login error:', error);
            console.error('Error details:', error.response?.data || error.message);
            throw error.response?.data || { message: 'Login failed' };
        }
    },

    register: async (userData) => {
        try {
            console.log('Attempting registration with:', userData);
            console.log('API URL:', `${API_URL}/api/auth/signup`);

            const response = await axios.post(`${API_URL}/api/auth/signup`, userData);

            console.log('Registration response:', response.data);

            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                console.log('Token saved to localStorage');
            }

            return response.data;
        } catch (error) {
            console.error('Registration error:', error);
            console.error('Error details:', error.response?.data || error.message);
            throw error.response?.data || { message: 'Registration failed' };
        }
    },

    logout: () => {
        localStorage.removeItem('token');
    },

    getCurrentUser: async () => {
        try {
            const token = localStorage.getItem('token');
            console.log('Getting current user with token:', token ? 'Token exists' : 'No token');

            if (!token) return null;

            console.log('API URL:', `${API_URL}/api/auth/me`);

            const response = await axios.get(`${API_URL}/api/auth/me`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            console.log('Current user response:', response.data);
            return response.data;
        } catch (error) {
            console.error('Get current user error:', error);
            console.error('Error details:', error.response?.data || error.message);
            localStorage.removeItem('token');
            return null;
        }
    },

    isAuthenticated: () => {
        return !!localStorage.getItem('token');
    },

    getAuthHeader: () => {
        const token = localStorage.getItem('token');
        return token ? { Authorization: `Bearer ${token}` } : {};
    }
};

export default authService;