/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'dtic-bg': '#0f172a',        // Slate 900
        'dtic-card': '#1e293b',      // Slate 800  
        'dtic-border': '#334155',    // Slate 700
      },
    },
  },
  plugins: [],
}
