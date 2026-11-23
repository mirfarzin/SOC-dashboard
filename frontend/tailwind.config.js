/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: '#FAF8F5',
          100: '#F8F5EE',
          200: '#F3EEE3', // Primary canvas
          300: '#EBE5D8', // Recessed surface
          400: '#DDD6C8', // Subtle border
          500: '#C5BCAC',
          600: '#9B9080',
          700: '#6E685F', // Muted text
          800: '#423E38',
          900: '#2D2924', // Secondary charcoal
          950: '#111111', // Deep structure / Ink black
        },
        ink: {
          DEFAULT: '#111111',
          charcoal: '#2D2924',
          muted: '#6E685F',
        },
        severity: {
          critical: '#C0392B',
          'critical-bg': '#FDF2F2',
          'critical-border': '#F5B7B1',
          high: '#D35400',
          'high-bg': '#FDF6F0',
          'high-border': '#EDBB99',
          medium: '#B7791F',
          'medium-bg': '#FEFCF3',
          'medium-border': '#F6E05E',
          low: '#276749',
          'low-bg': '#F0FFF4',
          'low-border': '#9AE6B4',
          info: '#4A5568',
          'info-bg': '#F7FAFC',
          'info-border': '#CBD5E0',
        }
      },
      boxShadow: {
        'neu-raised': '6px 6px 14px rgba(195, 185, 168, 0.45), -6px -6px 14px rgba(255, 255, 255, 0.85)',
        'neu-sm': '3px 3px 8px rgba(195, 185, 168, 0.4), -3px -3px 8px rgba(255, 255, 255, 0.8)',
        'neu-lg': '10px 10px 24px rgba(195, 185, 168, 0.48), -10px -10px 24px rgba(255, 255, 255, 0.9)',
        'neu-pressed': 'inset 3px 3px 7px rgba(195, 185, 168, 0.45), inset -3px -3px 7px rgba(255, 255, 255, 0.85)',
        'neu-sunken': 'inset 2px 2px 5px rgba(195, 185, 168, 0.4), inset -2px -2px 5px rgba(255, 255, 255, 0.7)',
        'neu-pill': '2px 2px 5px rgba(195, 185, 168, 0.4), -2px -2px 5px rgba(255, 255, 255, 0.85)',
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          'sans-serif',
        ],
        mono: [
          '"JetBrains Mono"',
          '"SFMono-Regular"',
          'Menlo',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
    },
  },
  plugins: [],
}
