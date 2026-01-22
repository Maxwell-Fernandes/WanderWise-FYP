import api from './api';

export const authService = {
  // User registration
  async register(userData) {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  // User login
  async login(credentials) {
    const response = await api.post('/api/auth/login', credentials);
    const { access_token, refresh_token, user } = response.data;

    // Store tokens and user data
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
  },

  // Logout
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  // Get current user
  async getCurrentUser() {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  // Get stored user data
  getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};
