import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AxiosError } from 'axios';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      const axiosError = err as AxiosError<{detail?: string}>;
      setError(axiosError.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-50 via-white to-primary-50/10 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center">
          <h2 className="text-4xl font-serif font-bold text-slate-900 mb-4">
            Begin Your Journey
          </h2>
          <p className="text-lg text-slate-600 mb-8">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500 transition-colors duration-300">
              Sign in here
            </Link>
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-6 py-4 rounded-xl text-sm font-medium">
                {error}
              </div>
            )}

            <div className="space-y-6">
              <div>
                <label htmlFor="full_name" className="block text-base font-medium text-slate-900 mb-2">
                  Full Name
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  required
                  className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-slate-800 placeholder-slate-400 transition-all duration-300"
                  placeholder="John Doe"
                  value={formData.full_name}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-base font-medium text-slate-900 mb-2">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-slate-800 placeholder-slate-400 transition-all duration-300"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-base font-medium text-slate-900 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  minLength={6}
                  className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-slate-800 placeholder-slate-400 transition-all duration-300"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                />
                <p className="mt-2 text-sm text-slate-500">Must be at least 6 characters</p>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-4 text-base font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <span className="inline-flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    Creating your account...
                  </span>
                ) : (
                  'Create your account'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
