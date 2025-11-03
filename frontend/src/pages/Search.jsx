import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { booksAPI } from '../services/api';

const Search = () => {
  const [searchData, setSearchData] = useState({
    description: '',
    additional_details: '',
  });
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setSearchData({
      ...searchData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setSearched(true);

    try {
      const response = await booksAPI.search(searchData);
      setBooks(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to search books');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectBook = (book) => {
    navigate('/checkout', { state: { book } });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Search for Books</h1>

          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                What are you looking for? *
              </label>
              <input
                id="description"
                name="description"
                type="text"
                required
                className="input-field"
                placeholder="e.g., sci-fi novels, mystery thrillers, coming-of-age stories"
                value={searchData.description}
                onChange={handleChange}
              />
              <p className="mt-1 text-sm text-gray-500">
                Describe the type of books you're interested in
              </p>
            </div>

            <div>
              <label
                htmlFor="additional_details"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Additional Details (optional)
              </label>
              <textarea
                id="additional_details"
                name="additional_details"
                rows="3"
                className="input-field"
                placeholder="e.g., written by female authors, set in the 1920s, with strong character development"
                value={searchData.additional_details}
                onChange={handleChange}
              />
              <p className="mt-1 text-sm text-gray-500">
                Add more specific criteria like author, time period, themes, etc.
              </p>
            </div>

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? (
                <span className="flex items-center">
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Searching...
                </span>
              ) : (
                'Search Books'
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-8">
            {error}
          </div>
        )}

        {/* Results */}
        {searched && !loading && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Search Results ({books.length} books found)
            </h2>

            {books.length === 0 ? (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No books found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search criteria and search again.
                </p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-6">
                {books.map((book, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition cursor-pointer"
                    onClick={() => handleSelectBook(book)}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-xl font-bold text-gray-900 flex-1">{book.title}</h3>
                      <span className="ml-2 px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
                        {book.type}
                      </span>
                    </div>

                    <p className="text-gray-700 mb-2">
                      <span className="font-medium">Author:</span> {book.author}
                    </p>

                    <p className="text-gray-700 mb-3">
                      <span className="font-medium">Published:</span> {book.year}
                    </p>

                    <p className="text-gray-600 text-sm mb-4">{book.description}</p>

                    <button className="btn-primary w-full text-sm">
                      Select this Book
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Search;