import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true, // Forza l'uso della porta 5173
    watch: {
      usePolling: true,
      interval: 1000,
    },
    // Questa è la parte importante per il WebSocket
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
      clientPort: 5173, // Forza il client a usare questa porta
    },
    // Aggiungi questa sezione per permettere connessioni da qualsiasi host
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      '.localhost', // Permette tutti i subdomini di localhost
    ],
  },
})