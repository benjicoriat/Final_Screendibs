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
      <div className="text-center py-12">
        <div className="mb-4">
          <svg
            className="mx-auto h-16 w-16 text-green-500"
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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Payment Successful!</h2>
        <p className="text-gray-600 mb-4">
          Your report is being generated and will be sent to your email shortly.
        </p>
        <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Card Information
        </label>
        <div className="border border-gray-300 rounded-lg p-3">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#424770',
                  '::placeholder': {
                    color: '#aab7c4',
                  },
                },
                invalid: {
                  color: '#9e2146',
                },
              },
            }}
          />
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Test card: 4242 4242 4242 4242 | Any future date | Any 3 digits
        </p>
      </div>

      <button
        type="submit"
        disabled={!stripe || processing}
        className="w-full btn-primary"
      >
        {processing ? 'Processing...' : `Pay $${amount.toFixed(2)}`}
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

  useEffect(() => {
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

  if (!book) {
    return null;
  }

  const selectedPlanData = plans.find((p) => p.type === selectedPlan);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Book & Plan Selection */}
          <div>
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Book Details</h2>
              <div className="space-y-2">
                <p className="text-gray-700">
                  <span className="font-medium">Title:</span> {book.title}
                </p>
                <p className="text-gray-700">
                  <span className="font-medium">Author:</span> {book.author}
                </p>
                <p className="text-gray-700">
                  <span className="font-medium">Published:</span> {book.year}
                </p>
                <p className="text-gray-700">
                  <span className="font-medium">Type:</span> {book.type}
                </p>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Select Plan</h2>

              {loading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <div className="space-y-3">
                  {plans.map((plan) => (
                    <label
                      key={plan.type}
                      className={`block border-2 rounded-lg p-4 cursor-pointer transition ${
                        selectedPlan === plan.type
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
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
                          <h3 className="font-bold text-gray-900">{plan.name}</h3>
                          <p className="text-sm text-gray-600">{plan.pages}</p>
                        </div>
                        <span className="text-xl font-bold text-primary-600">
                          ${plan.price.toFixed(2)}
                        </span>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Payment Form */}
          <div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Payment Information</h2>

              {selectedPlanData && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">Plan:</span>
                    <span className="font-medium">{selectedPlanData.name}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold">
                    <span>Total:</span>
                    <span className="text-primary-600">${selectedPlanData.price.toFixed(2)}</span>
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