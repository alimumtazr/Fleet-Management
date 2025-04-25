import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  currentRide: null,
  rideHistory: [],
  loading: false,
  error: null,
};

const rideSlice = createSlice({
  name: 'ride',
  initialState,
  reducers: {
    setCurrentRide: (state, action) => {
      state.currentRide = action.payload;
    },
    addToHistory: (state, action) => {
      state.rideHistory.push(action.payload);
    },
    setRideHistory: (state, action) => {
      state.rideHistory = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const {
  setCurrentRide,
  addToHistory,
  setRideHistory,
  setLoading,
  setError,
} = rideSlice.actions;

export default rideSlice.reducer; 