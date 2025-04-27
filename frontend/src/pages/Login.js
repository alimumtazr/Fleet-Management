import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    Container,
    Paper,
    Typography,
    TextField,
    Button,
    Box,
    Alert,
    Link,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import authService from '../services/authService';

const StyledPaper = styled(Paper)(({ theme }) => ({
    marginTop: theme.spacing(8),
    padding: theme.spacing(4),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
}));

const Login = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // Check for URL parameters
    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);

        // Handle session expired
        if (searchParams.get('session_expired') === 'true') {
            setError('Your session has expired. Please log in again.');
        }

        // Handle general authentication errors
        if (searchParams.get('error') === 'true') {
            setError('Authentication failed. Please log in again.');
        }

        // Clear the URL parameters after reading them
        if (searchParams.toString()) {
            navigate('/login', { replace: true });
        }
    }, [location, navigate]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Client-side validation
        if (!formData.email || !formData.email.includes('@')) {
            setError('Please enter a valid email address');
            return;
        }

        if (!formData.password) {
            setError('Please enter your password');
            return;
        }

        setLoading(true);

        try {
            const user = await authService.login(formData.email, formData.password);
            console.log("Login successful:", user);

            // Navigate based on user type
            if (user && user.user && user.user.user_type === 'driver') {
                navigate('/driver-dashboard');
            } else {
                navigate('/');
            }
        } catch (err) {
            console.error('Login error in component:', err);

            // Format the error message for display
            let errorMessage = 'Login failed. Please try again.';

            if (err.message) {
                // Check for specific error messages
                if (err.message.includes('Incorrect email or password')) {
                    errorMessage = 'Incorrect email or password. Please try again.';
                } else {
                    errorMessage = `Login failed: ${err.message}`;
                }
            }

            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container component="main" maxWidth="xs">
            <StyledPaper elevation={3}>
                <Typography component="h1" variant="h5">
                    Sign in
                </Typography>
                {error && (
                    <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
                        {error}
                    </Alert>
                )}
                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="email"
                        label="Email Address"
                        name="email"
                        autoComplete="email"
                        autoFocus
                        value={formData.email}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="password"
                        label="Password"
                        type="password"
                        id="password"
                        autoComplete="current-password"
                        value={formData.password}
                        onChange={handleChange}
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                        disabled={loading}
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </Button>
                    <Box sx={{ textAlign: 'center' }}>
                        <Link href="/register" variant="body2">
                            {"Don't have an account? Sign Up"}
                        </Link>
                    </Box>
                </Box>
            </StyledPaper>
        </Container>
    );
};

export default Login;