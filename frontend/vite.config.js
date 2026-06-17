import { defineConfig } from "vite";

// django-vite serves built assets under Django's STATIC_URL ("/static/").
// In dev, the Vite dev server runs on 5173 and Django proxies the tags to it.
export default defineConfig({
  base: "/static/",
  build: {
    manifest: true,
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: "src/main.js",
        admin: "src/admin.js",
      },
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    origin: "http://localhost:5173",
  },
});
