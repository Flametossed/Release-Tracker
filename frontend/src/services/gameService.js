import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data?.detail || 'Server error occurred');
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

export const gameService = {
  async getUpcomingGames(daysAhead = 90, limit = 100, platformIds = null, forceRefresh = false) {
    const params = new URLSearchParams({
      days_ahead: daysAhead.toString(),
      limit: limit.toString(),
    });
    
    if (platformIds && platformIds.length > 0) {
      params.append('platform_ids', platformIds.join(','));
    }
    
    if (forceRefresh) {
      params.append('force_refresh', 'true');
    }
    
    return await api.get(`/api/games/upcoming?${params.toString()}`);
  },

  async searchGames(query, limit = 20) {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    
    return await api.get(`/api/games/search?${params.toString()}`);
  },

  async getPlatforms(forceRefresh = false) {
    const params = new URLSearchParams();
    
    if (forceRefresh) {
      params.append('force_refresh', 'true');
    }
    
    const queryString = params.toString();
    const url = queryString ? `/api/platforms?${queryString}` : '/api/platforms';
    
    return await api.get(url);
  },

  async syncData() {
    return await api.post('/api/sync');
  },

  async healthCheck() {
    return await api.get('/api/health');
  },
};