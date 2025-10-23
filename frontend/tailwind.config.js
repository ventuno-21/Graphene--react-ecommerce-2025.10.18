/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            boxShadow: {
                'inner-md': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.1)',
                'inner-lg': 'inset 0 4px 6px 0 rgba(0, 0, 0, 0.15)',
            },
        },
    },
    plugins: [],
};