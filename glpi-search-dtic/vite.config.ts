import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    server: {
      port: 3000,
      host: '0.0.0.0',
      proxy: {
        '/api/dtic': {
          target: 'http://localhost:8003',
          changeOrigin: true,
          // Rewrite: /api/dtic/xxx -> /dtic/xxx (mantém dtic prefix se backend esperar, ou remove se backend esperar raiz)
          // No caso do glpi-dtic-api, routers são montados em /dtic ou raiz?
          // Routers em api.py: include_router(..., prefix="/dtic") ou prefix manual?
          // Verificamos antes: routers em api.py (glpi-sync-dtic) TÊM prefixo.
          // Mas Nginx faz mapping /api/dtic/ -> /dtic/.
          // Vite proxy target localhost:8003. Request /api/dtic/foo -> localhost:8003/api/dtic/foo (default).
          // Precisamos rewrite ^/api/dtic -> /dtic
          rewrite: (path) => path.replace(/^\/api\/dtic/, '/dtic')
        }
      }
    },
    plugins: [react()],
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    }
  };
});
