import { create } from 'zustand';
import { mockItinerary, mockInterests, mockPlaces } from '../data/mockData';

const useItineraryStore = create((set, get) => ({
  currentItinerary: null,
  itineraries: [],
  interests: [],
  isLoading: false,
  error: null,

  // Classify user interests from text (dummy)
  classifyInterests: async (preferenceText) => {
    set({ isLoading: true, error: null });
    return new Promise((resolve) => {
      setTimeout(() => {
        // Mock interest classification based on input text
        const detectedInterests = Object.keys(mockInterests).filter(key => 
          preferenceText.toLowerCase().includes(key.toLowerCase())
        );
        
        const result = {
          interests: detectedInterests.length > 0 ? detectedInterests : ['beaches', 'food'],
          confidence_scores: mockInterests,
        };
        
        set({
          interests: result.interests,
          isLoading: false,
        });
        
        resolve(result);
      }, 1500);
    });
  },

  // Create new itinerary (dummy)
  createItinerary: async (itineraryData) => {
    set({ isLoading: true, error: null });
    return new Promise((resolve) => {
      setTimeout(() => {
        // Modify mock itinerary with user input
        const customizedItinerary = {
          ...mockItinerary,
          num_days: itineraryData.numDays,
          start_date: itineraryData.startDate,
          budget_category: itineraryData.budgetCategory,
          daily_hours: {
            start: itineraryData.startTime,
            end: itineraryData.endTime,
          },
          user_interests: ['beaches', 'food', 'nature'], // Mock interests
          total_pois: mockItinerary.days.reduce((sum, day) => sum + day.places.length, 0),
          daily_itineraries: mockItinerary.days.slice(0, itineraryData.numDays),
        };
        
        set({
          currentItinerary: customizedItinerary,
          isLoading: false,
        });
        
        resolve(customizedItinerary);
      }, 3000);
    });
  },

  // Get itinerary by ID (dummy)
  getItinerary: async (itineraryId) => {
    set({ isLoading: true, error: null });
    return new Promise((resolve) => {
      setTimeout(() => {
        set({
          currentItinerary: mockItinerary,
          isLoading: false,
        });
        resolve(mockItinerary);
      }, 1000);
    });
  },

  // Get user's itineraries (dummy)
  getUserItineraries: async (userId) => {
    set({ isLoading: true, error: null });
    return new Promise((resolve) => {
      setTimeout(() => {
        const userItineraries = [
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
        
        set({
          itineraries: userItineraries,
          isLoading: false,
        });
        
        resolve(userItineraries);
      }, 1000);
    });
  },

  // Submit feedback (dummy)
  submitFeedback: async (itineraryId, feedbackData) => {
    set({ isLoading: true, error: null });
    return new Promise((resolve) => {
      setTimeout(() => {
        set({ isLoading: false });
        resolve({ success: true, message: 'Feedback submitted successfully' });
      }, 500);
    });
  },

  // Clear current itinerary
  clearCurrentItinerary: () => set({ currentItinerary: null }),

  // Clear error
  clearError: () => set({ error: null }),
}));

export default useItineraryStore;
