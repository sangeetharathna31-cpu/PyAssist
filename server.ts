import "dotenv/config";
import { spawn, ChildProcess } from "child_process";
import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";
import http from "http";

const PORT = parseInt(process.env.PORT || "5000", 10);
const PYTHON_PORT = 8888;
const PYTHON_HOST = "127.0.0.1";

let uvicornProcess: ChildProcess | null = null;

// Start Uvicorn Python backend
function startUvicorn(): ChildProcess {
  console.log(`[PyAssist] Starting Uvicorn backend on ${PYTHON_HOST}:${PYTHON_PORT}...`);
  const proc = spawn(
    "python3",
    [
      "-m",
      "uvicorn",
      "pyassist.app.main:app",
      "--host",
      PYTHON_HOST,
      "--port",
      PYTHON_PORT.toString()
    ],
    {
      stdio: "inherit",
      env: {
        ...process.env,
        PYTHONUNBUFFERED: "1"
      }
    }
  );

  proc.on("error", (err) => {
    console.error("[PyAssist] Failed to start Python backend:", err);
  });

  proc.on("exit", (code, signal) => {
    console.log(`[PyAssist] Python backend stopped with code ${code} (${signal})`);
  });

  return proc;
}

uvicornProcess = startUvicorn();

// Clean up child process on exit
function cleanup() {
  if (uvicornProcess) {
    console.log("[PyAssist] Shutting down Python backend...");
    try {
      uvicornProcess.kill("SIGTERM");
    } catch {
      // ignore
    }
    uvicornProcess = null;
  }
}

process.on("SIGINT", () => {
  cleanup();
  process.exit(0);
});

process.on("SIGTERM", () => {
  cleanup();
  process.exit(0);
});

process.on("exit", () => {
  cleanup();
});

const app = express();

// Wait for Python backend readiness
async function waitForPythonReady(maxWaitMs = 15000): Promise<boolean> {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    try {
      const res = await fetch(`http://${PYTHON_HOST}:${PYTHON_PORT}/api/health`);
      if (res.ok) {
        console.log("[PyAssist] Python FastAPI backend is healthy and responding.");
        return true;
      }
    } catch {
      // still starting
    }
    await new Promise((resolve) => setTimeout(resolve, 300));
  }
  console.warn("[PyAssist] Timeout waiting for Python backend readiness, proceeding anyway.");
  return false;
}

// Proxy all requests directly to Python FastAPI
const proxy = createProxyMiddleware({
  target: `http://${PYTHON_HOST}:${PYTHON_PORT}`,
  changeOrigin: true,
  ws: true,
  on: {
    error: (err: any, req: any, res: any) => {
      console.error("[PyAssist Proxy] Connection error:", err.message);
      if (!res.headersSent && typeof res.writeHead === "function") {
        res.writeHead(502, { "Content-Type": "text/html" });
        res.end(`
          <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h2>Starting PyAssist Backend...</h2>
            <p>The Python FastAPI service is initializing. Please refresh in a moment.</p>
          </div>
        `);
      }
    }
  }
});

app.use("/", proxy);

const server = app.listen(PORT, "0.0.0.0", async () => {
  console.log(`[PyAssist] Server running on http://0.0.0.0:${PORT}`);
  await waitForPythonReady();
});
