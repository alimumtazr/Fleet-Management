import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Box,
  IconButton,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const Payments = () => {
  const [paymentMethods, setPaymentMethods] = useState([
    {
      id: 1,
      type: 'Credit Card',
      last4: '4242',
      expiry: '12/25',
      isDefault: true,
    },
    {
      id: 2,
      type: 'Debit Card',
      last4: '5678',
      expiry: '06/24',
      isDefault: false,
    },
  ]);

  const [showAddForm, setShowAddForm] = useState(false);
  const [newPayment, setNewPayment] = useState({
    type: '',
    number: '',
    expiry: '',
    cvv: '',
  });

  const handleDelete = (id) => {
    setPaymentMethods(paymentMethods.filter((method) => method.id !== id));
  };

  const handleAddPayment = (e) => {
    e.preventDefault();
    // Handle adding new payment method
    console.log('New payment method:', newPayment);
    setShowAddForm(false);
    setNewPayment({
      type: '',
      number: '',
      expiry: '',
      cvv: '',
    });
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Payment Methods
        </Typography>

        {/* Existing Payment Methods */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {paymentMethods.map((method) => (
            <Grid item xs={12} sm={6} md={4} key={method.id}>
              <Card>
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Typography variant="h6">{method.type}</Typography>
                    <IconButton
                      color="error"
                      onClick={() => handleDelete(method.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                  <Typography variant="body1">
                    **** **** **** {method.last4}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Expires: {method.expiry}
                  </Typography>
                  {method.isDefault && (
                    <Typography variant="caption" color="primary">
                      Default Payment Method
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Add New Payment Method */}
        {!showAddForm ? (
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setShowAddForm(true)}
          >
            Add Payment Method
          </Button>
        ) : (
          <Paper sx={{ p: 3, mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Add New Payment Method
            </Typography>
            <form onSubmit={handleAddPayment}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Card Type"
                    value={newPayment.type}
                    onChange={(e) =>
                      setNewPayment({ ...newPayment, type: e.target.value })
                    }
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Card Number"
                    value={newPayment.number}
                    onChange={(e) =>
                      setNewPayment({ ...newPayment, number: e.target.value })
                    }
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Expiry Date"
                    value={newPayment.expiry}
                    onChange={(e) =>
                      setNewPayment({ ...newPayment, expiry: e.target.value })
                    }
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="CVV"
                    value={newPayment.cvv}
                    onChange={(e) =>
                      setNewPayment({ ...newPayment, cvv: e.target.value })
                    }
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={() => setShowAddForm(false)}
                    >
                      Cancel
                    </Button>
                    <Button type="submit" variant="contained">
                      Add Card
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </form>
          </Paper>
        )}
      </Paper>
    </Container>
  );
};

export default Payments; 