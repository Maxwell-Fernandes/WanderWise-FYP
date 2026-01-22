import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  Alert,
  Slider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Grid,
  CircularProgress,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import useItineraryStore from '../../stores/itineraryStore';
import useAuthStore from '../../stores/authStore';

const ItineraryForm = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const preferenceText = location.state?.preferenceText || '';

  const { user } = useAuthStore();
  const { createItinerary, isLoading, error } = useItineraryStore();

  const [formData, setFormData] = useState({
    preference_text: preferenceText,
    num_days: 3,
    start_date: new Date(),
    daily_start_time: '09:00',
    daily_end_time: '18:00',
    budget_category: 'moderate',
  });

  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  const handleDateChange = (date) => {
    setFormData({
      ...formData,
      start_date: date,
    });
  };

  const handleDaysChange = (event, newValue) => {
    setFormData({
      ...formData,
      num_days: newValue,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!user) {
      navigate('/login');
      return;
    }

    try {
      // Format date to YYYY-MM-DD
      const formattedData = {
        ...formData,
        start_date: formData.start_date.toISOString().split('T')[0],
      };

      const itinerary = await createItinerary(formattedData);
      // Navigate to the itinerary view page
      navigate(`/itinerary/${itinerary.itinerary_id}`);
    } catch (error) {
      console.error('Itinerary creation error:', error);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="md">
        <Box sx={{ mt: 4, mb: 4 }}>
          <Paper elevation={3} sx={{ p: 4 }}>
            <Typography component="h1" variant="h4" align="center" gutterBottom>
              Create Your Itinerary
            </Typography>
            <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
              Customize your trip details and let our AI create the perfect plan for you
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                {/* Number of Days */}
                <Grid item xs={12}>
                  <Typography gutterBottom>Number of Days: {formData.num_days}</Typography>
                  <Slider
                    value={formData.num_days}
                    onChange={handleDaysChange}
                    min={1}
                    max={7}
                    marks
                    step={1}
                    valueLabelDisplay="auto"
                    disabled={isLoading}
                  />
                </Grid>

                {/* Start Date */}
                <Grid item xs={12} sm={6}>
                  <DatePicker
                    label="Start Date"
                    value={formData.start_date}
                    onChange={handleDateChange}
                    minDate={new Date()}
                    disabled={isLoading}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Grid>

                {/* Daily Start Time */}
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Daily Start Time"
                    type="time"
                    value={formData.daily_start_time}
                    onChange={handleChange('daily_start_time')}
                    InputLabelProps={{ shrink: true }}
                    disabled={isLoading}
                  />
                </Grid>

                {/* Daily End Time */}
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Daily End Time"
                    type="time"
                    value={formData.daily_end_time}
                    onChange={handleChange('daily_end_time')}
                    InputLabelProps={{ shrink: true }}
                    disabled={isLoading}
                  />
                </Grid>

                {/* Budget Category */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <FormLabel component="legend">Budget Category</FormLabel>
                    <RadioGroup
                      row
                      value={formData.budget_category}
                      onChange={handleChange('budget_category')}
                    >
                      <FormControlLabel
                        value="budget"
                        control={<Radio />}
                        label="Budget (Economical)"
                        disabled={isLoading}
                      />
                      <FormControlLabel
                        value="moderate"
                        control={<Radio />}
                        label="Moderate (Balanced)"
                        disabled={isLoading}
                      />
                      <FormControlLabel
                        value="luxury"
                        control={<Radio />}
                        label="Luxury (Premium)"
                        disabled={isLoading}
                      />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Preferences Summary */}
                {preferenceText && (
                  <Grid item xs={12}>
                    <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Your Preferences:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {preferenceText}
                      </Typography>
                    </Paper>
                  </Grid>
                )}

                {/* Submit Button */}
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={isLoading}
                    startIcon={isLoading && <CircularProgress size={20} />}
                  >
                    {isLoading
                      ? 'Creating your perfect itinerary...'
                      : 'Generate Itinerary'}
                  </Button>
                  {isLoading && (
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      align="center"
                      display="block"
                      sx={{ mt: 2 }}
                    >
                      This may take 30-60 seconds as we optimize your route using advanced
                      algorithms...
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Box>
      </Container>
    </LocalizationProvider>
  );
};

export default ItineraryForm;
