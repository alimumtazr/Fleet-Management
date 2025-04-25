import React, { useState } from 'react';
import {
  TextField,
  Autocomplete,
  CircularProgress,
  Box,
  Typography,
} from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import { debounce } from 'lodash';

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org/search';
const LAHORE_BOUNDS = {
  north: 31.7012,
  south: 31.3924,
  east: 74.4787,
  west: 74.2287,
};

const LocationSearchInput = ({ label, onChange, value, sx }) => {
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Debounced function to fetch location suggestions
  const fetchSuggestions = debounce(async (input) => {
    if (!input || input.length < 3) {
      setOptions([]);
      return;
    }

    try {
      setLoading(true);
      const params = new URLSearchParams({
        q: `${input}, Lahore`,
        format: 'json',
        limit: 5,
        viewbox: `${LAHORE_BOUNDS.west},${LAHORE_BOUNDS.north},${LAHORE_BOUNDS.east},${LAHORE_BOUNDS.south}`,
        bounded: 1,
      });

      const response = await fetch(`${NOMINATIM_BASE_URL}?${params}`);
      const data = await response.json();

      const locations = data.map(item => ({
        description: item.display_name,
        coordinates: [parseFloat(item.lat), parseFloat(item.lon)],
        placeId: item.place_id,
      }));

      setOptions(locations);
    } catch (error) {
      console.error('Error fetching locations:', error);
      setOptions([]);
    } finally {
      setLoading(false);
    }
  }, 500);

  const handleInputChange = (event, newInputValue) => {
    setInputValue(newInputValue);
    fetchSuggestions(newInputValue);
  };

  const handleChange = (event, newValue) => {
    onChange?.(newValue);
  };

  return (
    <Autocomplete
      id="location-search-input"
      freeSolo
      options={options}
      getOptionLabel={(option) => 
        typeof option === 'string' ? option : option.description
      }
      value={value}
      onChange={handleChange}
      inputValue={inputValue}
      onInputChange={handleInputChange}
      loading={loading}
      filterOptions={(x) => x}
      sx={sx}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          variant="outlined"
          fullWidth
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <React.Fragment>
                {loading ? (
                  <CircularProgress color="inherit" size={20} />
                ) : null}
                {params.InputProps.endAdornment}
              </React.Fragment>
            ),
          }}
        />
      )}
      renderOption={(props, option) => (
        <li {...props}>
          <Box
            component="span"
            sx={{
              display: 'flex',
              alignItems: 'center',
              width: '100%',
            }}
          >
            <LocationOnIcon sx={{ color: 'text.secondary', mr: 1 }} />
            <Box>
              <Typography variant="body1">
                {option.description.split(',')[0]}
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ fontSize: '0.8rem' }}
              >
                {option.description.split(',').slice(1).join(',')}
              </Typography>
            </Box>
          </Box>
        </li>
      )}
    />
  );
};

export default LocationSearchInput; 