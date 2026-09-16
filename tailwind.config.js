/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        blueprint: {
          bg: "#0B2545",
          deep: "#071A33",
          panel: "#0F2E52",
          line: "#24507A",
          mist: "#8ECAE6",
        },
        paper: "#F4F7FB",
        amber: {
          DEFAULT: "#FFB84D",
          dim: "#D99A3B",
        },
        coral: "#EF6461",
      },
      fontFamily: {
        sans: ['"Space Grotesk"', "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
    },
  },
  plugins: [],
}
