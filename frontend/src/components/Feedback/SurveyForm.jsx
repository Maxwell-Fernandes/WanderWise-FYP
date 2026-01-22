import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  Alert,
  Slider,
  TextField,
  Grid,
} from '@mui/material';
import useItineraryStore from '../../stores/itineraryStore';

// P1-P16 Survey Questions
const LIKERT_QUESTIONS = [
  { code: 'P1', question: 'How satisfied are you with the overall itinerary?' },
  { code: 'P2', question: 'The recommended POIs matched my interests well' },
  { code: 'P3', question: 'The travel distances between POIs were reasonable' },
  { code: 'P4', question: 'The time allocation for each POI was appropriate' },
  { code: 'P5', question: 'The system understood my preferences accurately' },
  { code: 'P6', question: 'The daily schedule was realistic and achievable' },
  { code: 'P7', question: 'The opening hours and time windows were respected' },
  { code: 'P8', question: 'How would you rate the variety of POI categories?' },
  { code: 'P9', question: 'The popularity ratings helped me make decisions' },
  { code: 'P10', question: 'The clustering of POIs by day made geographical sense' },
  { code: 'P11', question: 'I would use this system again for trip planning' },
  { code: 'P12', question: 'The system was easy to use' },
  { code: 'P13', question: 'The itinerary saved me planning time' },
  { code: 'P14', question: 'I would recommend this system to others' },
];

const TEXT_QUESTIONS = [
  { code: 'P15', question: 'What did you like most about the generated itinerary?' },
  { code: 'P16', question: 'What improvements would you suggest?' },
];

const LIKERT_LABELS = {
  1: 'Strongly Disagree',
  2: 'Disagree',
  3: 'Neutral',
  4: 'Agree',
  5: 'Strongly Agree',
};

const SurveyForm = () => {
  const { itineraryId } = useParams();
  const navigate = useNavigate();
  const { submitFeedback, isLoading } = useItineraryStore();

  const [responses, setResponses] = useState({
    // Initialize Likert responses with neutral (3)
    ...Object.fromEntries(LIKERT_QUESTIONS.map((q) => [q.code, 3])),
    // Initialize text responses as empty strings
    ...Object.fromEntries(TEXT_QUESTIONS.map((q) => [q.code, ''])),
  });

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleLikertChange = (code) => (event, newValue) => {
    setResponses({
      ...responses,
      [code]: newValue,
    });
  };

  const handleTextChange = (code) => (event) => {
    setResponses({
      ...responses,
      [code]: event.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate text responses
    if (!responses.P15 || !responses.P16) {
      setError('Please answer both text questions');
      return;
    }

    try {
      await submitFeedback(itineraryId, {
        responses,
      });
      setSubmitted(true);
      setTimeout(() => {
        navigate('/');
      }, 3000);
    } catch (error) {
      setError('Failed to submit feedback. Please try again.');
      console.error('Survey submission error:', error);
    }
  };

  if (submitted) {
    return (
      <Container maxWidth="md">
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <Paper elevation={3} sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom color="primary">
              Thank You!
            </Typography>
            <Typography variant="body1">
              Your feedback has been submitted successfully. It will help us improve the
              system for future users.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Redirecting to home page...
            </Typography>
          </Paper>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Itinerary Feedback Survey
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
            Your feedback helps us improve the system. Please rate your experience.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            {/* Likert Scale Questions (P1-P14) */}
            {LIKERT_QUESTIONS.map((item, index) => (
              <Box key={item.code} sx={{ mb: 4 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {item.code}. {item.question}
                </Typography>
                <Box sx={{ px: 2 }}>
                  <Slider
                    value={responses[item.code]}
                    onChange={handleLikertChange(item.code)}
                    min={1}
                    max={5}
                    step={1}
                    marks={Object.entries(LIKERT_LABELS).map(([value, label]) => ({
                      value: parseInt(value),
                      label: window.innerWidth > 600 ? label : value,
                    }))}
                    valueLabelDisplay="auto"
                  />
                </Box>
              </Box>
            ))}

            {/* Text Questions (P15-P16) */}
            {TEXT_QUESTIONS.map((item) => (
              <Box key={item.code} sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {item.code}. {item.question}
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={responses[item.code]}
                  onChange={handleTextChange(item.code)}
                  placeholder="Please share your thoughts..."
                  required
                />
              </Box>
            ))}

            {/* Submit Button */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{ mt: 3 }}
            >
              {isLoading ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default SurveyForm;
