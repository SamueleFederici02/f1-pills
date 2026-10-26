/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        f1: {
          dark: '#0a0c10',
          card: 'rgba(20, 24, 33, 0.82)',
          border: 'rgba(255, 255, 255, 0.08)',
          red: '#e10600',
          yellow: '#facc15',
          purple: '#a855f7',
          green: '#22c55e',
          cyan: '#06b6d4',
          orange: '#f97316'
        }
      },
      fontFamily: {
        f1: ['"Formula1 Display"', 'system-ui', 'sans-serif'],
        sans: ['"Inter"', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}
