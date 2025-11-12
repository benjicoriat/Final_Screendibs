import axios from 'axios';

// Use VITE_API_URL if provided, otherwise use the proxy path
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

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
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getCurrentUser: () => api.get('/auth/me'),
};

// Books API
export const booksAPI = {
  search: (searchData) => api.post('/books/search', searchData),
};

// Payments API
export const paymentsAPI = {
  getPlans: () => api.get('/payments/plans'),
  createPaymentIntent: (paymentData) => api.post('/payments/create-payment-intent', paymentData),
  confirmPayment: (paymentId) => api.post(`/payments/confirm-payment/${paymentId}`),
  getHistory: () => api.get('/payments/history'),
};

export default api;