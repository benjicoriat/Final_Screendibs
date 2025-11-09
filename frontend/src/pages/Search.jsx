import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { MagnifyingGlassIcon, BookOpenIcon, AcademicCapIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
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
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-primary-50/10 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Search Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-4xl md:text-5xl font-serif font-bold text-slate-900 mb-6 leading-tight">
            Find Your Next
            <span className="block mt-2 bg-gradient-to-r from-primary-600 to-primary-500 bg-clip-text text-transparent">
              Literary Journey
            </span>
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Let our AI guide you to the perfect literary analysis, tailored to your interests
          </p>
        </motion.div>

        {/* Search Form */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-lg p-8 mb-16 max-w-3xl mx-auto border border-slate-100"
        >
          <div className="flex items-center space-x-8 mb-10">
            <div className="flex-1 h-px bg-slate-200"></div>
            <div className="flex space-x-8">
              <span className="flex items-center text-slate-600 hover:text-primary-500 transition-colors duration-300">
                <BookOpenIcon className="h-6 w-6 mr-3" />
                <span className="font-medium">Explore</span>
              </span>
              <span className="flex items-center text-slate-600 hover:text-primary-500 transition-colors duration-300">
                <AcademicCapIcon className="h-6 w-6 mr-3" />
                <span className="font-medium">Learn</span>
              </span>
              <span className="flex items-center text-slate-600 hover:text-primary-500 transition-colors duration-300">
                <SparklesIcon className="h-6 w-6 mr-3" />
                <span className="font-medium">Analyze</span>
              </span>
            </div>
            <div className="flex-1 h-px bg-slate-200"></div>
          </div>

          <form onSubmit={handleSearch} className="space-y-8">
            <div>
              <label htmlFor="description" className="block text-lg font-medium text-slate-900 mb-3">
                What kind of book are you looking for?
              </label>
              <div className="relative">
                <textarea
                  id="description"
                  name="description"
                  rows={4}
                  className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-slate-800 placeholder-slate-400 resize-none transition-all duration-300"
                  placeholder="E.g., 'A dystopian novel that explores themes of technology and surveillance' or 'A historical fiction set during World War II focusing on resistance movements'"
                  value={searchData.description}
                  onChange={handleChange}
                  required
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="additional_details" className="block text-lg font-medium text-slate-900 mb-3">
                Additional Details (Optional)
              </label>
              <input
                type="text"
                id="additional_details"
                name="additional_details"
                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-slate-800 placeholder-slate-400 transition-all duration-300"
                placeholder="Specific preferences: genre, time period, writing style, etc."
                value={searchData.additional_details}
                onChange={handleChange}
              />
            </div>

            <div className="flex justify-center mt-8">
              <motion.button
                type="submit"
                whileHover={{ scale: 1.02, boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)" }}
                whileTap={{ scale: 0.98 }}
                className={`inline-flex items-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-xl shadow-sm transition-all duration-300 ${
                  loading ? 'opacity-75 cursor-not-allowed' : ''
                }`}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    <span>Discovering Books...</span>
                  </>
                ) : (
                  <>
                    <MagnifyingGlassIcon className="mr-3 h-6 w-6" />
                    <span>Find Literary Treasures</span>
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-50 border border-red-200 text-red-600 px-6 py-4 rounded-xl mb-8 max-w-3xl mx-auto shadow-sm"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {searched && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="bg-white rounded-2xl shadow-lg p-8 border border-slate-100"
            >
              <h2 className="text-3xl font-serif font-bold text-slate-900 mb-8">
                Discovered {books.length} Literary Works
              </h2>

              {books.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-16"
                >
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
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                  <h3 className="mt-4 text-xl font-serif font-bold text-slate-800">No Books Found</h3>
                  <p className="mt-2 text-slate-600 max-w-md mx-auto">
                    Try adjusting your search criteria for a different literary adventure.
                  </p>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="grid md:grid-cols-2 gap-8"
                >
                  {books.map((book, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="group relative bg-white border border-slate-100 rounded-xl p-6 hover:shadow-lg transition-all duration-300 cursor-pointer"
                      onClick={() => handleSelectBook(book)}
                    >
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-serif font-bold text-slate-900 flex-1 group-hover:text-primary-600 transition-colors duration-300">
                          {book.title}
                        </h3>
                        <span className="ml-3 px-3 py-1 bg-gradient-to-r from-primary-50 to-primary-100 text-primary-700 text-xs font-medium rounded-full">
                          {book.type}
                        </span>
                      </div>

                      <p className="text-slate-700 mb-2">
                        <span className="font-medium text-slate-900">Author:</span>{' '}
                        <span className="text-slate-700">{book.author}</span>
                      </p>

                      <p className="text-slate-700 mb-4">
                        <span className="font-medium text-slate-900">Published:</span>{' '}
                        <span className="text-slate-700">{book.year}</span>
                      </p>

                      <p className="text-slate-600 text-sm mb-6 line-clamp-3">{book.description}</p>

                      <div className="absolute bottom-6 left-6 right-6">
                        <button className="w-full px-4 py-3 text-sm font-medium text-white bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 rounded-lg shadow-sm hover:shadow-md transition-all duration-300 group-hover:scale-[1.02]">
                          Analyze This Book
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Search;