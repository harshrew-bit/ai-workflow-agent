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
          50: '#FFFDFB',
          100: '#FFF9F5',
          200: '#FAF4F0',
          300: '#F4ECE6',
        },
        blush: {
          100: '#FDEEE8',
          200: '#FBE6DC',
          300: '#F7D8D0',
          400: '#ECC0B5',
        },
        charcoal: {
          900: '#211D1B',
          800: '#292522',
          700: '#38322F',
          600: '#4A4340',
          500: '#625A57',
          400: '#8A817D',
          300: '#B5ABA6',
          200: '#D6CBC6',
          100: '#E7D8D0',
        },
        brand: {
          blue: '#2563EB',
          magenta: '#C026D3',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      boxShadow: {
        warm: '0 4px 20px -2px rgba(98, 90, 87, 0.08), 0 2px 6px -1px rgba(98, 90, 87, 0.04)',
        'warm-lg': '0 10px 25px -3px rgba(98, 90, 87, 0.12), 0 4px 10px -2px rgba(98, 90, 87, 0.06)',
      },
    },
  },
  plugins: [],
}
