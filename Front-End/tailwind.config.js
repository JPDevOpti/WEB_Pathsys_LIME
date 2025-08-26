/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Colores LIME del sistema hospitalario
        'LIME-Azul-Claro': '#CAEAF2',
        'LIME-Azul-2': '#8FC8DE',
        'LIME-Azul-3': '#5CA6C9',
        'LIME-Azul-4': '#2974A3',
        'LIME-Azul-Oscuro': '#064D5F',
        
        // Colores de marca (verdes)
        brand: {
          25: '#f2f7ff',
          50: '#ecf3ff',
          100: '#E6FAEC',
          200: '#E6FAEC',
          300: '#B3EBC7',
          400: '#A4EAB5',
          500: '#7FCB97',
          600: '#7FCB97',
          700: '#3D8D5B',
          800: '#3D8D5B',
          900: '#3D8D5B',
          950: '#161950',
        },
        
        // Colores azul claro
        'blue-light': {
          25: '#f5fbff',
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e6fe',
          300: '#7cd4fd',
          400: '#36bffa',
          500: '#0ba5ec',
          600: '#0086c9',
          700: '#026aa2',
          800: '#065986',
          900: '#0b4a6f',
          950: '#062c41',
        },
        
        // Colores de estado
        success: {
          25: '#f6fef9',
          50: '#ecfdf3',
          100: '#d1fadf',
          200: '#a6f4c5',
          300: '#6ce9a6',
          400: '#32d583',
          500: '#12b76a',
          600: '#039855',
          700: '#027a48',
          800: '#05603a',
          900: '#054f31',
          950: '#053321',
        },
        
        error: {
          25: '#fffbfa',
          50: '#fef3f2',
          100: '#fee4e2',
          200: '#fecdca',
          300: '#fda29b',
          400: '#f97066',
          500: '#f04438',
          600: '#d92d20',
          700: '#b42318',
          800: '#912018',
          900: '#7a271a',
          950: '#55160c',
        },
        
        warning: {
          25: '#fffcf5',
          50: '#fffaeb',
          100: '#fef0c7',
          200: '#fedf89',
          300: '#fec84b',
          400: '#fdb022',
          500: '#f79009',
          600: '#dc6803',
          700: '#b54708',
          800: '#93370d',
          900: '#7a2e0e',
          950: '#4e1d09',
        },
        
        // Colores de tema adicionales
        'theme-pink': {
          500: '#ee46bc',
        },
        
        'theme-purple': {
          500: '#7a5af8',
        },
      },
      
      fontFamily: {
        sans: ['Outfit', 'ui-sans-serif', 'system-ui'],
        outfit: ['Outfit', 'sans-serif'],
      },
      
      fontSize: {
        'title-2xl': ['72px', '90px'],
        'title-xl': ['60px', '72px'],
        'title-lg': ['48px', '60px'],
        'title-md': ['36px', '44px'],
        'title-sm': ['30px', '38px'],
        'theme-xl': ['20px', '30px'],
        'theme-sm': ['14px', '20px'],
        'theme-xs': ['12px', '18px'],
      },
      
      boxShadow: {
        'theme-xs': '0px 1px 2px 0px rgba(16, 24, 40, 0.05)',
        'theme-sm': '0px 1px 3px 0px rgba(16, 24, 40, 0.1), 0px 1px 2px 0px rgba(16, 24, 40, 0.06)',
        'theme-md': '0px 4px 8px -2px rgba(16, 24, 40, 0.1), 0px 2px 4px -2px rgba(16, 24, 40, 0.06)',
        'theme-lg': '0px 12px 16px -4px rgba(16, 24, 40, 0.08), 0px 4px 6px -2px rgba(16, 24, 40, 0.03)',
        'theme-xl': '0px 20px 24px -4px rgba(16, 24, 40, 0.08), 0px 8px 8px -4px rgba(16, 24, 40, 0.03)',
        'focus-ring': '0px 0px 0px 4px rgba(70, 95, 255, 0.12)',
        'slider-navigation': '0px 1px 2px 0px rgba(16, 24, 40, 0.1), 0px 1px 3px 0px rgba(16, 24, 40, 0.1)',
        'tooltip': '0px 4px 6px -2px rgba(16, 24, 40, 0.05), -8px 0px 20px 8px rgba(16, 24, 40, 0.05)',
      },
      
      dropShadow: {
        '4xl': ['0 35px 35px rgba(0, 0, 0, 0.25)', '0 45px 65px rgba(0, 0, 0, 0.15)'],
      },
      spacing: {
        '4.5': '1.125rem',
        '5.5': '1.375rem',
        '6.5': '1.625rem',
        '7.5': '1.875rem',
        '15': '3.75rem',
        '17': '4.25rem',
        '18': '4.5rem',
        '19': '4.75rem',
        '20': '5rem',
        '21': '5.25rem',
        '22': '5.5rem',
        '25': '6.25rem',
        '30': '7.5rem',
        '35': '8.75rem',
        '40': '10rem',
        '45': '11.25rem',
        '50': '12.5rem',
        '55': '13.75rem',
        '60': '15rem',
        '65': '16.25rem',
        '70': '17.5rem',
        '72': '18rem',
        '75': '18.75rem',
        '80': '20rem',
        '85': '21.25rem',
        '90': '22.5rem',
        '95': '23.75rem',
        '100': '25rem',
      },
      zIndex: {
        '999': '999',
        '9999': '9999',
        '99999': '99999',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}