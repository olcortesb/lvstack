import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    proxy: {
      '/_ministack': 'http://localhost:4566',
      '/_localstack': 'http://localhost:4566',
      '/_robotocore': 'http://localhost:4569',
    }
  }
})
