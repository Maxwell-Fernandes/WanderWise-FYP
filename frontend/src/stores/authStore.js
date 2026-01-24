import { create } from 'zustand';
import { authService } from '../services/auth';

// Mock user data for testing
const mockUser = {
  id: '1',
  email: 'demo@wanderwise.com',
  full_name: 'Demo User',
  username: 'demo_user',
};

const useAuthStore = create((set) => ({
  user: mockUser, //authService.getUser(),
  isAuthenticated: true, //authService.isAuthenticated(),
  isLoading: false,
  error: null,

  // Login action
  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authService.login(credentials);
      set({
        user: data.user,
        isAuthenticated: true,
        isLoading: false,
      });
      return data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      });
      throw error;
    }
  },

  // Register action
  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authService.register(userData);
      set({ isLoading: false });
      return data;
    } catch (error) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      });
      throw error;
    }
  },

  // Logout action
  logout: () => {
    authService.logout();
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    });
  },

  // Clear error
  clearError: () => set({ error: null }),
}));

export default useAuthStore;
