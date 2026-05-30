/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        paper: '#f8fafc',
        ink: '#0f172a',
        line: '#e2e8f0',
        moss: '#4f46e5',
        coral: '#f97316',
        saffron: '#facc15',
        cloud: '#f1f5f9',
        ocean: '#2563eb',
        violet: '#7c3aed'
      }
    }
  },
  plugins: []
}
