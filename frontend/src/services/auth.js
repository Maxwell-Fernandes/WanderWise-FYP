// Dummy authentication service for frontend-only MVP
export const authService = {
  // User registration (dummy)
  async register(userData) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockUser = {
          id: '1',
          username: userData.username,
          email: userData.email,
          full_name: userData.full_name || userData.username,
        };
        resolve({
          access_token: 'dummy-access-token',
          refresh_token: 'dummy-refresh-token',
          user: mockUser,
        });
      }, 1000);
    });
  },

  // User login (dummy)
  async login(credentials) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockUser = {
          id: '1',
          username: credentials.email.split('@')[0],
          email: credentials.email,
          full_name: 'Traveler',
        };
        resolve({
          access_token: 'dummy-access-token',
          refresh_token: 'dummy-refresh-token',
          user: mockUser,
        });
      }, 1000);
    });
  },

  // Logout
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  // Get current user (dummy)
  async getCurrentUser() {
    return new Promise((resolve) => {
      setTimeout(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
          resolve(JSON.parse(storedUser));
        } else {
          resolve(null);
        }
      }, 500);
    });
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
