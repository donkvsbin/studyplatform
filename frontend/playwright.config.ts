import { defineConfig } from "@playwright/test";
import { resolve } from "node:path";
const python = resolve(
  process.platform === "win32"
    ? "../backend/.venv/Scripts/python.exe"
    : "../backend/.venv/bin/python",
);
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:5174",
    locale: "zh-CN",
    viewport: { width: 1440, height: 1000 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command: `"${python}" ../scripts/e2e_server.py`,
      url: "http://127.0.0.1:5001/api/v1/health",
      reuseExistingServer: false,
      timeout: 30000,
    },
    {
      command: "npm run dev -- --port 5174",
      url: "http://127.0.0.1:5174",
      reuseExistingServer: false,
      env: { E2E: "1" },
      timeout: 30000,
    },
  ],
});
