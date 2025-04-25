import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Alert,
  CircularProgress,
  Grid,
  Divider,
} from '@mui/material';
import { useDispatch } from 'react-redux';
import { processPayment } from '../../store/slices/paymentSlice';

const PAYMENT_METHODS = {
  EASYPAISA: 'easypaisa',
  HBL: 'hbl',
  CASH: 'cash',
};

const PaymentForm = ({ amount, rideId, onSuccess }) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState(PAYMENT_METHODS.EASYPAISA);
  const [formData, setFormData] = useState({
    phoneNumber: '',
    accountNumber: '',
    otp: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePaymentMethodChange = (e) => {
    setPaymentMethod(e.target.value);
    setFormData({
      phoneNumber: '',
      accountNumber: '',
      otp: '',
    });
  };

  const validateForm = () => {
    if (paymentMethod === PAYMENT_METHODS.CASH) return true;

    if (paymentMethod === PAYMENT_METHODS.EASYPAISA) {
      return formData.phoneNumber.length === 11;
    }

    if (paymentMethod === PAYMENT_METHODS.HBL) {
      return formData.accountNumber.length === 16;
    }

    return false;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) {
      setError('Please fill in all required fields correctly');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const paymentData = {
        rideId,
        amount,
        method: paymentMethod,
        ...formData,
      };

      await dispatch(processPayment(paymentData)).unwrap();
      onSuccess?.();
    } catch (error) {
      setError(error.message || 'Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderPaymentFields = () => {
    switch (paymentMethod) {
      case PAYMENT_METHODS.EASYPAISA:
        return (
          <TextField
            margin="normal"
            required
            fullWidth
            name="phoneNumber"
            label="EasyPaisa Mobile Number"
            type="tel"
            value={formData.phoneNumber}
            onChange={handleChange}
            inputProps={{
              maxLength: 11,
              pattern: '[0-9]*',
            }}
            helperText="Enter 11 digit mobile number"
          />
        );

      case PAYMENT_METHODS.HBL:
        return (
          <TextField
            margin="normal"
            required
            fullWidth
            name="accountNumber"
            label="HBL Account Number"
            value={formData.accountNumber}
            onChange={handleChange}
            inputProps={{
              maxLength: 16,
              pattern: '[0-9]*',
            }}
            helperText="Enter 16 digit account number"
          />
        );

      default:
        return null;
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h5" gutterBottom className="gradient-text">
        Payment Details
      </Typography>

      <Box sx={{ my: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h4" className="gradient-text">
              Rs. {amount.toFixed(2)}
            </Typography>
          </Grid>
        </Grid>
      </Box>

      <Divider sx={{ my: 2 }} />

      <form onSubmit={handleSubmit}>
        <FormControl component="fieldset" sx={{ width: '100%', mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Select Payment Method
          </Typography>
          <RadioGroup
            name="paymentMethod"
            value={paymentMethod}
            onChange={handlePaymentMethodChange}
          >
            <FormControlLabel
              value={PAYMENT_METHODS.EASYPAISA}
              control={<Radio />}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <img
                    src="/assets/easypaisa-logo.png"
                    alt="EasyPaisa"
                    style={{ height: 24, marginRight: 8 }}
                  />
                  <Typography>EasyPaisa</Typography>
                </Box>
              }
            />
            <FormControlLabel
              value={PAYMENT_METHODS.HBL}
              control={<Radio />}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <img
                    src="/assets/hbl-logo.png"
                    alt="HBL"
                    style={{ height: 24, marginRight: 8 }}
                  />
                  <Typography>HBL Bank</Typography>
                </Box>
              }
            />
            <FormControlLabel
              value={PAYMENT_METHODS.CASH}
              control={<Radio />}
              label="Cash Payment"
            />
          </RadioGroup>
        </FormControl>

        {renderPaymentFields()}

        {error && (
          <Alert severity="error" sx={{ mt: 2, mb: 2 }}>
            {error}
          </Alert>
        )}

        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={loading || !validateForm()}
          sx={{
            mt: 3,
            mb: 2,
            py: 1.5,
            borderRadius: 2,
            background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
          }}
        >
          {loading ? (
            <CircularProgress size={24} />
          ) : (
            `Pay Rs. ${amount.toFixed(2)}`
          )}
        </Button>
      </form>
    </Paper>
  );
};

export default PaymentForm; 