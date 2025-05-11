import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Paper,
    Typography,
    TextField,
    Button,
    Box,
    Alert,
    Link,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
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

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        user_type: 'customer',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

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
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters long');
            return;
        }

        if (!formData.email || !formData.email.includes('@')) {
            setError('Please enter a valid email address');
            return;
        }

        if (!formData.first_name || !formData.last_name) {
            setError('Please enter your first and last name');
            return;
        }

        setLoading(true);
        try {
            const { confirmPassword, phone_number, ...userData } = formData;
            const user = await authService.register(userData);
            console.log("Registration successful:", user);

            // Navigate based on user type
            // Fix: Access user_type from the nested user object in the response
            if (user && user.user && user.user.user_type === 'driver') {
                navigate('/driver-dashboard');
            } else {
                navigate('/');
            }
        } catch (err) {
            console.error('Registration error in component:', err);

            // Format the error message for display
            let errorMessage = 'Registration failed. Please try again.';

            if (err.message) {
                // Check for specific error messages
                if (err.message.includes('Email already registered')) {
                    errorMessage = 'This email is already registered. Please use a different email or try logging in.';
                } else {
                    errorMessage = `Registration failed: ${err.message}`;
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
                    Sign up
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
                        autoComplete="new-password"
                        value={formData.password}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="confirmPassword"
                        label="Confirm Password"
                        type="password"
                        id="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="first_name"
                        label="First Name"
                        id="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="last_name"
                        label="Last Name"
                        id="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                    />
                    <FormControl fullWidth margin="normal">
                        <InputLabel id="user-type-label">User Type</InputLabel>
                        <Select
                            labelId="user-type-label"
                            id="user_type"
                            name="user_type"
                            value={formData.user_type}
                            label="User Type"
                            onChange={handleChange}
                        >
                            <MenuItem value="customer">Customer</MenuItem>
                            <MenuItem value="rider">Rider</MenuItem>
                            <MenuItem value="driver">Driver</MenuItem>
                        </Select>
                    </FormControl>
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                        disabled={loading}
                    >
                        {loading ? 'Signing up...' : 'Sign Up'}
                    </Button>
                    <Box sx={{ textAlign: 'center' }}>
                        <Link href="/login" variant="body2">
                            Already have an account? Sign in
                        </Link>
                    </Box>
                </Box>
            </StyledPaper>
        </Container>
    );
};

export default Register;