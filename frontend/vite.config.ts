import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  optimizeDeps: { include: ["markdown-it", "dompurify"] },
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": process.env.E2E
        ? "http://127.0.0.1:5001"
        : "http://127.0.0.1:5000",
    },
  },
});
