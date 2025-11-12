import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
// @ts-expect-error - api.js exports are available at runtime
import { paymentsAPI } from '../services/api.js';

interface Payment {
  id: number;
  user_id: number;
  stripe_payment_id: string;
  amount: number;
  plan_type: 'basic' | 'detailed' | 'premium';
  book_title: string;
  book_author: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  pdf_sent: boolean;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPaymentHistory();
  }, []);

  const fetchPaymentHistory = async () => {
    try {
      const response = await paymentsAPI.getHistory();
      setPayments(response.data);
    } catch (err) {
      setError('Failed to load payment history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-primary-50/10 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8 mb-10">
          <h1 className="text-4xl font-serif font-bold text-slate-900 mb-4">
            Welcome back, <span className="text-primary-600">{user?.full_name || user?.email}</span>!
          </h1>
          <p className="text-lg text-slate-600 mb-6">
            Ready to dive into another literary analysis? Begin your next intellectual journey.
          </p>
          <div className="mt-6">
            <Link 
              to="/search" 
              className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
            >
              Explore Books
            </Link>
          </div>
        </div>

        {/* Payment History */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
          <h2 className="text-3xl font-serif font-bold text-slate-900 mb-8">Your Literary Journey</h2>

          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-14 w-14 border-b-2 border-primary-600"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-600 px-6 py-4 rounded-xl">
              {error}
            </div>
          ) : payments.length === 0 ? (
            <div className="text-center py-16">
              <svg
                className="mx-auto h-16 w-16 text-slate-300"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-4 text-xl font-serif font-bold text-slate-800">Begin Your Collection</h3>
              <p className="mt-2 text-slate-600 max-w-md mx-auto">
                Start your literary analysis journey by exploring our collection of books.
              </p>
              <div className="mt-8">
                <Link 
                  to="/search" 
                  className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
                >
                  Discover Books
                </Link>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100">
                      Book
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100">
                      Plan
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100">
                      Amount
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100">
                      Date
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-medium text-slate-500 uppercase tracking-wider border-b border-slate-100">
                      PDF Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {payments.map((payment) => (
                    <tr key={payment.id} className="hover:bg-slate-50 transition-colors duration-200">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-slate-900">
                          {payment.book_title}
                        </div>
                        <div className="text-sm text-slate-500">{payment.book_author}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-slate-700 capitalize">
                          {payment.plan_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-slate-900">
                          ${(payment.amount / 100).toFixed(2)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-3 py-1 text-xs font-medium rounded-full ${
                            payment.status === 'completed'
                              ? 'bg-green-50 text-green-700'
                              : payment.status === 'pending'
                              ? 'bg-amber-50 text-amber-700'
                              : 'bg-red-50 text-red-700'
                          }`}
                        >
                          {payment.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-slate-600">
                          {formatDate(payment.created_at)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {payment.pdf_sent ? (
                          <span className="text-green-600 flex items-center text-sm">
                            <svg
                              className="w-5 h-5 mr-2"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                            <span className="font-medium">Delivered</span>
                          </span>
                        ) : (
                          <span className="text-amber-600 flex items-center text-sm">
                            <svg
                              className="w-5 h-5 mr-2 animate-spin"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                              />
                            </svg>
                            <span className="font-medium">Processing</span>
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
