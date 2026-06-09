/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          900: "#1e3a8a",
        },
      },
      animation: {
        "float-wander": "floatWander 6s infinite alternate ease-in-out",
        "deep-thinking": "deepThinking 1.5s infinite ease-in-out",
        "float-aside": "floatAside 4s infinite alternate ease-in-out",
      },
      keyframes: {
        floatWander: {
          "0%": { transform: "translateY(0) translateX(0) rotate(0deg)" },
          "33%": { transform: "translateY(-30px) translateX(-40px) rotate(-10deg)" },
          "66%": { transform: "translateY(-10px) translateX(-20px) rotate(10deg)" },
          "100%": { transform: "translateY(-40px) translateX(-10px) rotate(-5deg)" },
        },
        deepThinking: {
          "0%": { transform: "translate(-50%,-50%) scale(1) rotate(0deg)" },
          "25%": { transform: "translate(-50%,-50%) scale(1.1) rotate(-15deg)" },
          "50%": { transform: "translate(-50%,-50%) scale(1.2) rotate(15deg)" },
          "75%": { transform: "translate(-50%,-50%) scale(1.1) rotate(-10deg)" },
          "100%": { transform: "translate(-50%,-50%) scale(1) rotate(0deg)" },
        },
        floatAside: {
          "0%": { transform: "translateY(0) rotate(0deg)" },
          "100%": { transform: "translateY(-12px) rotate(8deg)" },
        },
      },
    },
  },
  plugins: [],
};
