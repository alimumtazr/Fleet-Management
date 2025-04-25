import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  availableDrivers: [],
  currentDriver: null,
  earnings: {
    today: 0,
    total: 0,
  },
  schedule: [],
  loading: false,
  error: null,
};

const driverSlice = createSlice({
  name: 'driver',
  initialState,
  reducers: {
    setAvailableDrivers: (state, action) => {
      state.availableDrivers = action.payload;
    },
    setCurrentDriver: (state, action) => {
      state.currentDriver = action.payload;
    },
    updateEarnings: (state, action) => {
      state.earnings = {
        ...state.earnings,
        ...action.payload,
      };
    },
    setSchedule: (state, action) => {
      state.schedule = action.payload;
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
  setAvailableDrivers,
  setCurrentDriver,
  updateEarnings,
  setSchedule,
  setLoading,
  setError,
} = driverSlice.actions;

export default driverSlice.reducer; 