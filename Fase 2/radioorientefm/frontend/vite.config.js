import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

//https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  //url base del backend: usa vite_api_url si está definida, si no, fallback local
  const backendTarget = env.VITE_API_URL || 'http://127.0.0.1:8000'

  return {
    plugins: [react()],
    css: {
      modules: {
        localsConvention: 'camelCase',
      },
    },
    esbuild: {
      loader: 'jsx',
      include: /src\/.*\.[jt]sx?$/,
      exclude: []
    },
    optimizeDeps: {
      esbuildOptions: {
        loader: {
          '.js': 'jsx'
        }
      }
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
        '/api': {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        },
        '/dashboard': {
          target: backendTarget,
          changeOrigin: true,
          secure: false,
        }
      }
    },
    build: {
      outDir: 'build',
      sourcemap: true
    }
  }
})