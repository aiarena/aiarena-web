/** @type {import('tailwindcss').Config} */

const CustomHighlightVar = 'rgba(154, 255, 70, 1)';
const CustomPrimaryVar = 'rgba(134, 194, 50, 1)';

const CustomBackgroundColorVar = 'rgba(134, 194, 50, 1)';


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
        gugi: ['var(--font-gugi)', 'sans-serif'],
        
  
      },
      colors: {
        customGreen: CustomPrimaryVar,   
        
        customBackgroundColor1: 'rgba(42,48,57,1)',
        customBackgroundColor1D1: 'rgba(30,37,50,1)',
        customBackgroundColor1L1: 'rgba(60,61,79,1)',

        customBackgroundColor2: 'rgba(50,55,65,1)',   // Slightly brighter than customBackgroundColor1
        customBackgroundColor2D1: 'rgba(25,30,40,1)', // Darker than customBackgroundColor1D1
        customBackgroundColor2L1: 'rgba(70,75,85,1)', // Lighter version for a softer feel
        customBackgroundColor3: 'rgba(45,50,60,1)',   // Neutral shade for balanced sections
        customBackgroundColor3D1: 'rgba(20,25,35,1)', // Darker, muted variant for dramatic sections
        customBackgroundColor3L1: 'rgba(65,70,80,1)', // Softer, lighter variant



        customGreenHighlight1: 'rgba(255, 255, 0, 1)',       
        // customGreenHighlight1: 'rgba(0, 0, 255, 1)',           
        customGreenDarken1: 'rgba(104, 144, 20, 1)', 
        customGreenDarken2: 'rgba(84, 110, 15, 1)',    
        customGreenDarken3: 'rgba(64, 84, 5, 1)',      
        customGreenDarken9: 'rgba(0, 0, 0, 1)',      
        customWild: 'rgba(134, 254, 50, 1)',
        softTeal: '#32B3A4',
        mellowYellow: '#F5A623',
        darken: 'rgba(0, 0, 0, 0.3)',
   
        oldBg0: 'rgb(39,40,48)',
        oldBg1: 'rgb(43,44,52)',
        oldBg2: 'rgb(48,51,59)',
     
      },

      backgroundImage: {
        // 'fancy-cushion': "url('./backgrounds/fancy-cushion.png')",
        // 'fancy-background': "url('/fancy-cushion.png')",
        'gradient-green1': 'linear-gradient(90deg, rgba(134, 194, 50, 1) 0%, rgba(50, 120, 30, 1) 100%)',

        // Experimenting
        'gradient-green-lime': 'linear-gradient(90deg, rgba(97,137,47, 1) 0%, rgba(168,208,80, 1) 100%)',
        'gradient-green-olive': 'linear-gradient(90deg, rgba(97,137,47, 1) 0%, rgba(56,90,30, 1) 100%)',
        'gradient-green-yellow': 'linear-gradient(90deg, rgba(97,137,47, 1) 0%, rgba(245,229,108, 1) 100%)',
        'gradient-experimental-1': 'linear-gradient(135deg, rgba(97,137,47, 1) 0%, rgba(168,208,80, 1) 50%, rgba(245,229,108, 1) 100%)',
        'gradient-experimental-2': 'linear-gradient(90deg, rgba(97,137,47, 1) 0%, rgba(245,229,108, 0.8) 25%, rgba(168,208,80, 0.6) 75%, rgba(56,90,30, 1) 100%)',
        'gradient-experimental-3': 'linear-gradient(45deg, rgba(97,137,47, 1) 0%, rgba(245,229,108, 0.6) 30%, rgba(168,208,80, 0.9) 70%, rgba(97,137,47, 1) 100%)',
        'green-teal-gradient': 'linear-gradient(135deg, rgba(97,137,47, 1) 0%, #32B3A4 100%)',
        'green-yellow-gradient': 'linear-gradient(90deg, rgba(97,137,47, 1) 0%, #F5A623 100%)',
        'teal-yellow-gradient': 'linear-gradient(45deg, #32B3A4 0%, #F5A623 100%)',
      },



      borderColor: {
        customGreen: CustomPrimaryVar, 
        softTeal: '#32B3A4',
        mellowYellow: '#F5A623',
      },
      maxWidth: {
        '9xl': '96rem',
      },
      
      borderWidth: {
        '5': '5px',
        '10': '10px',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '2rem',
      },
      backgroundSize: {
        '25': '25px',
      },
      backgroundRepeat: {
        'repeat-custom': 'repeat',
      },
      boxShadow: {
        customDiscord: '0 5px 155px 5px rgba(88,101,242,0.9)', 
      },

    },
  },
  plugins: [
    function ({ addUtilities }) {
      const newUtilities = {
        '.bg-fancy-texture': {
          'background-size': '50px 50px',
          'background-repeat': 'repeat',
        },
        // '.bg-background-texture': {
        //   'background-image': `url('${getPublicPrefix()}/backgrounds/background.gif')`,
        //   'background-repeat': 'repeat',
        // },
      };
      addUtilities(newUtilities, ['responsive', 'hover']);
    },

    function ({ addBase }) {
      addBase({
        ':root': {
          '--customGreenHighlight1': CustomHighlightVar,
        },
      });
    },
  ],
}
