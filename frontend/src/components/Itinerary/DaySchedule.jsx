import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import {
  LocationOn,
  DirectionsCar,
  Schedule,
  AttachMoney,
} from '@mui/icons-material';
import { format } from 'date-fns';

const DaySchedule = ({ dayData }) => {
  if (!dayData || !dayData.schedule) {
    return <Typography>No schedule available for this day</Typography>;
  }

  const { date, schedule } = dayData;

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {date && `Day ${dayData.day} - ${format(new Date(date), 'MMMM d, yyyy')}`}
        </Typography>
      </Box>

      <Timeline position="alternate">
        {schedule.map((item, index) => (
          <TimelineItem key={index}>
            <TimelineOppositeContent
              sx={{ m: 'auto 0' }}
              align="right"
              variant="body2"
              color="text.secondary"
            >
              <Typography variant="body2" fontWeight="bold">
                {item.arrival_time}
              </Typography>
              <Typography variant="caption">Arrival</Typography>
            </TimelineOppositeContent>

            <TimelineSeparator>
              <TimelineConnector />
              <TimelineDot color="primary">
                <LocationOn />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>

            <TimelineContent sx={{ py: '12px', px: 2 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" component="span" gutterBottom>
                    {item.place.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {item.place.description}
                  </Typography>

                  <Box sx={{ mt: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                      <Schedule fontSize="small" sx={{ mr: 0.5 }} />
                      <Typography variant="body2" color="text.secondary">
                        Visit Duration: {item.visit_duration_minutes} min
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                      <Schedule fontSize="small" sx={{ mr: 0.5 }} />
                      <Typography variant="body2" color="text.secondary">
                        Depart: {item.departure_time}
                      </Typography>
                    </Box>

                    {item.travel_time_to_next_minutes > 0 && (
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        <DirectionsCar fontSize="small" sx={{ mr: 0.5 }} />
                        <Typography variant="caption" color="text.secondary">
                          {item.travel_time_to_next_minutes} min travel to next location
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>

      {/* Day Summary */}
      <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
        <Typography variant="subtitle2" gutterBottom>
          Day Summary:
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Total Places: {schedule.length} | Total Visit Time:{' '}
          {schedule.reduce((sum, item) => sum + item.visit_duration_minutes, 0)} minutes |
          Total Travel Time:{' '}
          {schedule.reduce(
            (sum, item) => sum + (item.travel_time_to_next_minutes || 0),
            0
          )}{' '}
          minutes
        </Typography>
      </Box>
    </Paper>
  );
};

export default DaySchedule;
