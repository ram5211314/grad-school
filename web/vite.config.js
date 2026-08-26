import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8080",
      "/recommendation": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/recommendation/, "")
      }
    }
  }
});
