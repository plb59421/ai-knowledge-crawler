import { defineConfig } from "vite";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const reportDataPath = resolve(__dirname, "../../knowledge_base/exports/data/report_latest.json");

export default defineConfig({
  base: "./",
  plugins: [
    {
      name: "local-report-data",
      configureServer(server) {
        server.middlewares.use("/report-data/report_latest.json", (_request, response, next) => {
          if (!existsSync(reportDataPath)) {
            next();
            return;
          }
          response.setHeader("Content-Type", "application/json; charset=utf-8");
          response.end(readFileSync(reportDataPath));
        });
      }
    }
  ],
  build: {
    outDir: "../../knowledge_base/exports/app",
    emptyOutDir: true
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true
      }
    },
    fs: {
      allow: [resolve(__dirname, "../..")]
    }
  }
});
