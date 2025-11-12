import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { paymentsAPI } from '../services/api';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY);

const CheckoutForm = ({ book, selectedPlan, amount }) => {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);
    setError('');

    try {
      // Create payment intent
      const response = await paymentsAPI.createPaymentIntent({
        plan_type: selectedPlan,
        book_title: book.title,
        book_author: book.author,
      });

      const { clientSecret, paymentId } = response.data;

      // Confirm payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(
        clientSecret,
        {
          payment_method: {
            card: elements.getElement(CardElement),
          },
        }
      );

      if (stripeError) {
        setError(stripeError.message);
        setProcessing(false);
        return;
      }

      if (paymentIntent.status === 'succeeded') {
        // Confirm payment on backend
        await paymentsAPI.confirmPayment(paymentId);
        setSuccess(true);

        setTimeout(() => {
          navigate('/dashboard');
        }, 3000);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Payment failed. Please try again.');
      setProcessing(false);
    }
  };

  if (success) {
    return (
      <div className="text-center py-16">
        <div className="mb-6">
          <svg
            className="mx-auto h-20 w-20 text-green-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h2 className="text-3xl font-serif font-bold text-slate-900 mb-4">Payment Successful!</h2>
        <p className="text-lg text-slate-600 mb-6">
          Your literary analysis is being crafted and will arrive in your inbox shortly.
        </p>
        <p className="text-sm font-medium text-slate-500">Redirecting to your dashboard...</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-6 py-4 rounded-xl text-sm font-medium">
          {error}
        </div>
      )}

      <div>
        <label className="block text-lg font-medium text-slate-900 mb-3">
          Card Information
        </label>
        <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-sm">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  fontWeight: '400',
                  color: '#334155',
                  '::placeholder': {
                    color: '#94A3B8',
                  },
                  ':-webkit-autofill': {
                    color: '#334155',
                  },
                },
                invalid: {
                  color: '#EF4444',
                  iconColor: '#EF4444',
                },
              },
            }}
          />
        </div>
        <p className="mt-3 text-sm text-slate-500">
          Test card: 4242 4242 4242 4242 | Any future date | Any 3 digits
        </p>
      </div>

      <button
        type="submit"
        disabled={!stripe || processing}
        className="w-full px-6 py-4 text-base font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {processing ? (
          <span className="inline-flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            Processing...
          </span>
        ) : (
          `Complete Payment - $${amount.toFixed(2)}`
        )}
      </button>
    </form>
  );
};

const Checkout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const book = location.state?.book;
  const [selectedPlan, setSelectedPlan] = useState('detailed');
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    const isGuest = localStorage.getItem('guestMode') === 'true';
    
    if (!token && isGuest) {
      // Guest trying to checkout - show auth prompt
      setShowAuthPrompt(true);
      return;
    }

    if (!book) {
      navigate('/search');
      return;
    }
    fetchPlans();
  }, [book, navigate]);

  const fetchPlans = async () => {
    try {
      const response = await paymentsAPI.getPlans();
      setPlans(response.data.plans);
    } catch (err) {
      console.error('Failed to fetch plans', err);
    } finally {
      setLoading(false);
    }
  };

  if (showAuthPrompt) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-50 via-white to-primary-50/10 py-12 px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-100 p-8 text-center">
          <div className="mb-6">
            <svg className="mx-auto h-16 w-16 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-serif font-bold text-slate-900 mb-4">
            Sign In Required
          </h2>
          <p className="text-slate-600 mb-6">
            To complete your purchase, please sign in or create an account.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/login')}
              className="w-full px-6 py-3 text-base font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate('/register')}
              className="w-full px-6 py-3 text-base font-medium text-slate-700 bg-white border-2 border-slate-300 hover:border-primary-500 hover:text-primary-600 rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
            >
              Create Account
            </button>
            <button
              onClick={() => navigate('/search')}
              className="w-full px-6 py-3 text-base font-medium text-slate-500 hover:text-slate-700 transition-colors duration-300"
            >
              Continue Browsing
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!book) {
    return null;
  }

  const selectedPlanData = plans.find((p) => p.type === selectedPlan);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-primary-50/10 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-serif font-bold text-slate-900 mb-12">Complete Your Order</h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Book & Plan Selection */}
          <div>
            <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8 mb-8">
              <h2 className="text-2xl font-serif font-bold text-slate-900 mb-6">Selected Book</h2>
              <div className="space-y-4">
                <p className="flex justify-between text-lg">
                  <span className="font-medium text-slate-500">Title</span>
                  <span className="text-slate-900">{book.title}</span>
                </p>
                <p className="flex justify-between text-lg">
                  <span className="font-medium text-slate-500">Author</span>
                  <span className="text-slate-900">{book.author}</span>
                </p>
                <p className="flex justify-between text-lg">
                  <span className="font-medium text-slate-500">Published</span>
                  <span className="text-slate-900">{book.year}</span>
                </p>
                <p className="flex justify-between text-lg">
                  <span className="font-medium text-slate-500">Category</span>
                  <span className="text-slate-900">{book.type}</span>
                </p>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
              <h2 className="text-2xl font-serif font-bold text-slate-900 mb-6">Choose Your Plan</h2>

              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <div className="space-y-4">
                  {plans.map((plan) => (
                    <label
                      key={plan.type}
                      className={`block border-2 rounded-xl p-6 cursor-pointer transition-all duration-300 ${
                        selectedPlan === plan.type
                          ? 'border-primary-500 bg-gradient-to-r from-primary-50 to-primary-100/50'
                          : 'border-slate-200 hover:border-primary-300 hover:bg-slate-50'
                      }`}
                    >
                      <input
                        type="radio"
                        name="plan"
                        value={plan.type}
                        checked={selectedPlan === plan.type}
                        onChange={(e) => setSelectedPlan(e.target.value)}
                        className="sr-only"
                      />
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900 mb-1">{plan.name}</h3>
                          <p className="text-slate-600">{plan.pages}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-primary-600">
                            ${plan.price.toFixed(2)}
                          </p>
                          <p className="text-sm text-slate-500">USD</p>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Payment Form */}
          <div>
            <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
              <h2 className="text-2xl font-serif font-bold text-slate-900 mb-6">Payment Details</h2>

              {selectedPlanData && (
                <div className="mb-8 p-6 bg-gradient-to-r from-slate-50 to-slate-100/50 rounded-xl border border-slate-200">
                  <div className="flex justify-between text-lg mb-2">
                    <span className="text-slate-600">Selected Plan</span>
                    <span className="font-medium text-slate-900">{selectedPlanData.name}</span>
                  </div>
                  <div className="flex justify-between items-end">
                    <span className="text-xl font-bold text-slate-900">Total Due</span>
                    <div className="text-right">
                      <span className="text-3xl font-bold text-primary-600">${selectedPlanData.price.toFixed(2)}</span>
                      <p className="text-sm text-slate-500 mt-1">USD</p>
                    </div>
                  </div>
                </div>
              )}

              <Elements stripe={stripePromise}>
                <CheckoutForm
                  book={book}
                  selectedPlan={selectedPlan}
                  amount={selectedPlanData?.price || 0}
                />
              </Elements>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;