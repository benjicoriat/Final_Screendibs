import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import { AuthResponse, Book, PaymentIntent, User } from '../types';

interface ErrorData {
  detail?: string;
}

// Default to a versioned API root; can be overridden with VITE_API_URL
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';

class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public data?: ErrorData
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class Api {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.instance.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ErrorData>) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        throw new ApiError(
          error.response?.status || 500,
          error.response?.data?.detail || 'An unexpected error occurred',
          error.response?.data
        );
      }
    );
  }

  private handleResponse<T>(response: AxiosResponse<T>): T {
    return response.data;
  }

  // Auth endpoints
  async register(userData: { email: string; password: string; full_name: string }): Promise<AuthResponse> {
    const response = await this.instance.post<AuthResponse>('/auth/register', userData);
    return this.handleResponse(response);
  }

  async login(credentials: { email: string; password: string }): Promise<AuthResponse> {
    const response = await this.instance.post<AuthResponse>('/auth/login', credentials);
    return this.handleResponse(response);
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.instance.get<User>('/auth/me');
    return this.handleResponse(response);
  }

  // Books endpoints
  async searchBooks(searchData: { query: string; filters?: Record<string, string> }): Promise<Book[]> {
    const response = await this.instance.post<Book[]>('/books/search', searchData);
    return this.handleResponse(response);
  }

  async getBook(id: string): Promise<Book> {
    const response = await this.instance.get<Book>(`/api/v1/books/${id}`);
    return this.handleResponse(response);
  }

  // Payments endpoints
  async createPaymentIntent(paymentData: { amount: number; currency: string }): Promise<PaymentIntent> {
    const response = await this.instance.post<PaymentIntent>('/payments/create-payment-intent', paymentData);
    return this.handleResponse(response);
  }

  async confirmPayment(paymentId: string): Promise<{ success: boolean }> {
    const response = await this.instance.post<{ success: boolean }>(`/payments/confirm-payment/${paymentId}`);
    return this.handleResponse(response);
  }

  async getPaymentHistory(): Promise<PaymentIntent[]> {
    const response = await this.instance.get<PaymentIntent[]>('/payments/history');
    return this.handleResponse(response);
  }
}

export const api = new Api();
export default api;