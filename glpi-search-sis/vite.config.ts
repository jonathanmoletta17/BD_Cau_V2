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
        '/api/sis': {
          target: 'http://localhost:8002',
          changeOrigin: true,
          // Rewrite: /api/sis/xxx -> /sis/xxx (necessário em Dev Mode se target for localhost:8002 que serve /sis prefix)
          // Mas depende: se uvicorn é iniciado na raiz e api inclui router /sis, então URL é localhost:8002/sis/xxx.
          // Se eu mando request /api/sis/xxx -> target/api/sis/xxx.
          // Precisamos rewrite para /sis/xxx se o backend tiver prefix.
          rewrite: (path) => path.replace(/^\/api\/sis/, '/sis')
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
