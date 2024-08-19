/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/_components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-quicksand)', 'sans-serif'],
      },
      colors: {
        customGreen: 'rgba(97,137,47, 1)',
     
      },

      backgroundImage: {
        'fancy-cushion': "url('/fancy-cushion.png')",
      },
      backgroundSize: {
        '25': '25px',
      },
      backgroundRepeat: {
        'repeat-custom': 'repeat',
      },


    },
  },
  plugins: [
    function ({ addUtilities }) {
      const newUtilities = {
        '.bg-fancy-texture': {
          'background-image': "url('/fancy-cushion.png')",
          'background-size': '25px 25px',
          'background-repeat': 'repeat',
        },
      };

      addUtilities(newUtilities, ['responsive', 'hover']);
    },
  ],
}
