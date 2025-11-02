import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/api/auth/register', userData),
  login: (credentials) => api.post('/api/auth/login', credentials),
  getCurrentUser: () => api.get('/api/auth/me'),
};

// Books API
export const booksAPI = {
  search: (searchData) => api.post('/api/books/search', searchData),
};

// Payments API
export const paymentsAPI = {
  getPlans: () => api.get('/api/payments/plans'),
  createPaymentIntent: (paymentData) => api.post('/api/payments/create-payment-intent', paymentData),
  confirmPayment: (paymentId) => api.post(`/api/payments/confirm-payment/${paymentId}`),
  getHistory: () => api.get('/api/payments/history'),
};

export default api;