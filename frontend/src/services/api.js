// Mock API service for frontend-only MVP
import { mockItinerary, mockInterests, mockPlaces, mockSurveyQuestions } from '../data/mockData';

const api = {
  get: async (url) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        let data = {};
        
        if (url.includes('/itineraries')) {
          if (url.includes('/itinerary/')) {
            // Get specific itinerary
            data = mockItinerary;
          } else {
            // Get user itineraries list
            data = [
              {
                id: 'itin-123',
                name: 'Goa Beach Tour',
                num_days: 3,
                created_at: '2024-11-29',
                total_distance_km: 145.6,
              },
              {
                id: 'itin-456',
                name: 'Cultural Heritage Tour',
                num_days: 2,
                created_at: '2024-11-28',
                total_distance_km: 89.2,
              },
            ];
          }
        } else if (url.includes('/places')) {
          data = mockPlaces;
        } else if (url.includes('/interests')) {
          data = mockInterests;
        } else if (url.includes('/survey')) {
          data = mockSurveyQuestions;
        }
        
        resolve({
          data,
          status: 200,
        });
      }, 500);
    });
  },

  post: async (url, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        let responseData = {};
        
        if (url.includes('/itineraries')) {
          // Create new itinerary
          responseData = {
            ...mockItinerary,
            num_days: data.numDays,
            start_date: data.startDate,
            budget_category: data.budgetCategory,
            daily_hours: {
              start: data.startTime,
              end: data.endTime,
            },
            user_interests: ['beaches', 'food', 'nature'],
            total_pois: mockItinerary.days.reduce((sum, day) => sum + day.places.length, 0),
            daily_itineraries: mockItinerary.days.slice(0, data.numDays),
          };
        } else if (url.includes('/classify-interests')) {
          // Classify interests
          responseData = {
            interests: ['beaches', 'food', 'nature'],
            confidence_scores: mockInterests,
          };
        } else if (url.includes('/feedback')) {
          // Submit feedback
          responseData = { success: true, message: 'Feedback submitted successfully' };
        }
        
        resolve({
          data: responseData,
          status: 201,
        });
      }, 1000);
    });
  },

  put: async (url, data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {},
          status: 200,
        });
      }, 500);
    });
  },

  delete: async (url) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {},
          status: 204,
        });
      }, 500);
    });
  },
};

export default api;
