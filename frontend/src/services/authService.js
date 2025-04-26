import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const authService = {
    login: async (email, password) => {
        try {
            const response = await axios.post(`${API_URL}/login`, {
                email,
                password
            });
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
            }
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Login failed' };
        }
    },

    register: async (userData) => {
        try {
            const response = await axios.post(`${API_URL}/register`, userData);
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
            }
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Registration failed' };
        }
    },

    logout: () => {
        localStorage.removeItem('token');
    },

    getCurrentUser: async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return null;

            const response = await axios.get(`${API_URL}/users/me`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            return response.data;
        } catch (error) {
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