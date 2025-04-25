import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import rideReducer from './slices/rideSlice';
import driverReducer from './slices/driverSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    ride: rideReducer,
    driver: driverReducer,
  },
});

export default store; 