import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Add a request interceptor to automatically add the token to all requests
axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        console.log('[Interceptor] Token from localStorage:', token ? `${token.substring(0, 10)}...` : 'null'); // Log token retrieval
        if (token) {
            // Make sure the token is properly formatted 
            const formattedToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
            config.headers.Authorization = formattedToken;
            console.log('[Interceptor] Setting Authorization header for URL:', config.url, 'Header:', config.headers.Authorization ? `${config.headers.Authorization.substring(0, 20)}...` : 'Not set'); // Log header setting
            
            // Only log API calls, not every axios request
            if (config.url.includes('/api/')) {
                console.log('Adding token to API request:', config.url);
            }

            // Add content type and accept headers for API requests
            if (config.url.includes('/api/')) {
                config.headers['Content-Type'] = 'application/json';
                config.headers['Accept'] = 'application/json';
            }
        }
        return config;
    },
    (error) => {
        console.error('[Interceptor] Request error:', error);
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

// Helper function to get auth header - define this before using it
const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    if (!token) return {};
    
    // Ensure token has 'Bearer ' prefix
    const formattedToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
    return { Authorization: formattedToken };
};

const authService = {
    login: async (email, password) => {
        try {
            console.log('Attempting login with:', { email, password: '******' });
            console.log('API URL:', `${API_URL}/api/auth/login`);

            const response = await axios.post(`${API_URL}/api/auth/login`, {
                email,
                password
            });

            console.log('Login response status:', response.status);

            // Standardize token storage regardless of how the backend sends it
            if (response.data && (response.data.access_token || response.data.token)) {
                // Get token from either format
                const token = response.data.access_token || response.data.token;
                
                // Always store the raw token without 'Bearer ' prefix
                localStorage.setItem('token', token);
                console.log('[Login] Token saved to localStorage:', token ? `${token.substring(0, 10)}...` : 'null'); // Log token saving
            } else {
                console.error('[Login] No token in response:', response.data);
            }
            
            return response.data;
        } catch (error) {
            // Error handling code remains the same
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
                } else if (error.response.data && error.response.data.error) {
                    errorMessage = error.response.data.error;
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

            console.log('Registration response status:', response.status);

            // Standardize token storage regardless of how the backend sends it
            if (response.data && (response.data.access_token || response.data.token)) {
                // Get token from either format
                const token = response.data.access_token || response.data.token;
                
                // Always store the raw token without 'Bearer ' prefix
                localStorage.setItem('token', token);
                console.log('Token saved to localStorage:', token.substring(0, 10) + '...');
            } else {
                console.error('No token in response:', response.data);
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
                } else if (error.response.data && error.response.data.error) {
                    errorMessage = error.response.data.error;
                }
                
                // If we have a status code, include it in the error
                if (error.response.status) {
                    console.error(`Error status: ${error.response.status}`);
                    
                    // Special handling for 409 Conflict (email already exists)
                    if (error.response.status === 409) {
                        errorMessage = 'This email is already registered. Please use a different email or try logging in.';
                    }
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
            console.log('[GetCurrentUser] Token from localStorage:', token ? `${token.substring(0, 10)}...` : 'null');

            if (!token) {
                console.log('[GetCurrentUser] No token found, returning null.');
                return null;
            }

            // Ensure token has Bearer prefix
            const formattedToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
            console.log('[GetCurrentUser] Formatted token:', formattedToken.substring(0, 20) + '...');

            const response = await axios.get(`${API_URL}/api/auth/me`, { 
                headers: {
                    'Authorization': formattedToken,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('[GetCurrentUser] Success:', response.data);
            return response.data;
        } catch (error) {
            console.error('[GetCurrentUser] Error:', error.response ? error.response.data : error.message);
            return null;
        }
    },

    isAuthenticated: () => {
        return !!localStorage.getItem('token');
    },

    getAuthHeader: getAuthHeader
};

export default authService;
