/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f3f0',
          100: '#e8e4db',
          200: '#d2c8b7',
          300: '#bba993',
          400: '#a58b70',
          500: '#8e6f4d',
          600: '#72583d',
          700: '#55422e',
          800: '#392c1f',
          900: '#1c160f',
        },
        accent: {
          50: '#f0f7f7',
          100: '#d9ebeb',
          200: '#b3d7d7',
          300: '#8dc3c3',
          400: '#67afaf',
          500: '#419b9b',
          600: '#347c7c',
          700: '#275d5d',
          800: '#1a3e3e',
          900: '#0d1f1f',
        },
        serif: {
          50: '#fcf5f5',
          100: '#f7e3e3',
          200: '#efc7c7',
          300: '#e7abab',
          400: '#df8f8f',
          500: '#d77373',
          600: '#ac5c5c',
          700: '#814545',
          800: '#562e2e',
          900: '#2b1717',
        }
      },
      fontFamily: {
        sans: ['Inter var', 'sans-serif'],
        serif: ['Crimson Pro', 'serif'],
        display: ['Playfair Display', 'serif'],
      },
      animation: {
        'fade-up': 'fadeUp 0.5s ease-out',
        'fade-down': 'fadeDown 0.5s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scale-up': 'scaleUp 0.2s ease-out',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleUp: {
          '0%': { transform: 'scale(0.95)' },
          '100%': { transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')],
  plugins: [],
}