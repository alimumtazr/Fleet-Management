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

// Add a response interceptor to handle token expiration
axios.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Handle 401 Unauthorized errors (token expired or invalid)
        if (error.response && error.response.status === 401) {
            console.log('Received 401 Unauthorized response, clearing token');

            // Don't clear token for login/register endpoints
            const url = error.config.url;
            if (!url.includes('/api/auth/login') && !url.includes('/api/auth/signup')) {
                localStorage.removeItem('token');

                // Redirect to login page if not already there
                if (window.location.pathname !== '/login') {
                    console.log('Redirecting to login page');
                    window.location.href = '/login?session_expired=true';
                }
            }
        }

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

            // Extract the error message from the response
            let errorMessage = 'Login failed';

            if (error.response) {
                console.error('Error response:', error.response);

                // Handle FastAPI error format
                if (error.response.data && error.response.data.detail) {
                    errorMessage = error.response.data.detail;
                }
                // Handle our custom error format
                else if (error.response.data && error.response.data.message) {
                    errorMessage = error.response.data.message;
                }
                // If we have a status code, include it in the error
                if (error.response.status) {
                    console.error(`Error status: ${error.response.status}`);

                    // Special handling for 401 Unauthorized
                    if (error.response.status === 401) {
                        errorMessage = 'Incorrect email or password';
                    }
                }
            }

            throw { message: errorMessage };
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

            // Extract the error message from the response
            let errorMessage = 'Registration failed';

            if (error.response) {
                console.error('Error response:', error.response);

                // Handle FastAPI error format
                if (error.response.data && error.response.data.detail) {
                    errorMessage = error.response.data.detail;
                }
                // Handle our custom error format
                else if (error.response.data && error.response.data.message) {
                    errorMessage = error.response.data.message;
                }
                // If we have a status code, include it in the error
                if (error.response.status) {
                    console.error(`Error status: ${error.response.status}`);
                }
            }

            throw { message: errorMessage };
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

            // Log detailed error information
            if (error.response) {
                console.error('Error response:', error.response);
                console.error('Error status:', error.response.status);
                console.error('Error data:', error.response.data);
            } else if (error.request) {
                console.error('Error request:', error.request);
            } else {
                console.error('Error message:', error.message);
            }

            // If we get a 401 or 403, the token is invalid or expired
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                console.log('Removing invalid token from localStorage');
                localStorage.removeItem('token');
            }

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