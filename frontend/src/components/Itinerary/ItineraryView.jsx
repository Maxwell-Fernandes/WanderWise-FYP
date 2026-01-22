import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  Stack,
  Divider,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  LocationOn,
  AccessTime,
  DirectionsCar,
  EventNote,
} from '@mui/icons-material';
import { useState } from 'react';
import useItineraryStore from '../../stores/itineraryStore';
import DaySchedule from './DaySchedule';

const ItineraryView = () => {
  const { itineraryId } = useParams();
  const { currentItinerary, getItinerary, isLoading, error } = useItineraryStore();
  const [selectedDay, setSelectedDay] = useState(0);

  useEffect(() => {
    if (itineraryId) {
      getItinerary(itineraryId);
    }
  }, [itineraryId]);

  const handleDayChange = (event, newValue) => {
    setSelectedDay(newValue);
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '60vh',
          }}
        >
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  if (!currentItinerary) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Alert severity="info">No itinerary found</Alert>
        </Box>
      </Container>
    );
  }

  const { daily_itineraries, user_interests, total_distance_km, total_pois, num_days } =
    currentItinerary;

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        {/* Header */}
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Your Personalized Goa Itinerary
          </Typography>

          {/* Interests */}
          {user_interests && user_interests.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Based on your interests:
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {user_interests.map((interest, index) => (
                  <Chip key={index} label={interest} color="primary" size="small" />
                ))}
              </Stack>
            </Box>
          )}

          {/* Summary Stats */}
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <EventNote color="primary" />
                <Typography variant="h6">{num_days}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Days
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <LocationOn color="primary" />
                <Typography variant="h6">{total_pois}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Places
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <DirectionsCar color="primary" />
                <Typography variant="h6">{total_distance_km?.toFixed(1)} km</Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Distance
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <AccessTime color="primary" />
                <Typography variant="h6">
                  {daily_itineraries?.[selectedDay]?.schedule?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Stops Today
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Day Tabs */}
        <Paper elevation={3} sx={{ mb: 3 }}>
          <Tabs
            value={selectedDay}
            onChange={handleDayChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            {daily_itineraries?.map((day, index) => (
              <Tab key={index} label={`Day ${day.day}`} />
            ))}
          </Tabs>
        </Paper>

        {/* Daily Schedule */}
        {daily_itineraries && daily_itineraries[selectedDay] && (
          <DaySchedule dayData={daily_itineraries[selectedDay]} />
        )}
      </Box>
    </Container>
  );
};

export default ItineraryView;
