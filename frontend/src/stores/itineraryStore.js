import { create } from 'zustand';
import api from '../services/api';

const useItineraryStore = create((set, get) => ({
  currentItinerary: null,
  itineraries: [],
  interests: [],
  isLoading: false,
  error: null,

  // Classify user interests from text
  classifyInterests: async (preferenceText) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post('/api/interests/classify', {
        text: preferenceText,
      });
      set({
        interests: response.data.interests,
        isLoading: false,
      });
      return response.data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Interest classification failed',
        isLoading: false,
      });
      throw error;
    }
  },

  // Create new itinerary
  createItinerary: async (itineraryData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post('/api/itinerary/create', itineraryData);
      set({
        currentItinerary: response.data,
        isLoading: false,
      });
      return response.data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Itinerary creation failed',
        isLoading: false,
      });
      throw error;
    }
  },

  // Get itinerary by ID
  getItinerary: async (itineraryId) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get(`/api/itinerary/${itineraryId}`);
      set({
        currentItinerary: response.data,
        isLoading: false,
      });
      return response.data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Failed to load itinerary',
        isLoading: false,
      });
      throw error;
    }
  },

  // Get user's itineraries
  getUserItineraries: async (userId) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get(`/api/itinerary/user/${userId}`);
      set({
        itineraries: response.data,
        isLoading: false,
      });
      return response.data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Failed to load itineraries',
        isLoading: false,
      });
      throw error;
    }
  },

  // Submit feedback
  submitFeedback: async (itineraryId, feedbackData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post(
        `/api/itinerary/${itineraryId}/feedback`,
        feedbackData
      );
      set({ isLoading: false });
      return response.data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Failed to submit feedback',
        isLoading: false,
      });
      throw error;
    }
  },

  // Clear current itinerary
  clearCurrentItinerary: () => set({ currentItinerary: null }),

  // Clear error
  clearError: () => set({ error: null }),
}));

export default useItineraryStore;
