import axios from 'axios';

// Base URL: In dev, Vite proxy forwards /api → http://localhost:5000/api
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  timeout: 30000,
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('uvvis_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally — redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('uvvis_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;
