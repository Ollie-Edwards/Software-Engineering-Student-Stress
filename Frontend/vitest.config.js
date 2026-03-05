import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['html', 'text-summary'],
      include: ['src/**/*.{js,ts,jsx,tsx}'],
      exclude: [
        'src/**/*.test.{js,ts,jsx,tsx}',
        'setupTests.js',
        'src/main.jsx',
      ],
    },
  },
})