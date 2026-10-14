# PyAssist on Replit

## Start the app

Run `npm run dev`. The Node.js gateway listens on `PORT` or port 5000 and starts the FastAPI backend on `127.0.0.1:8888`. The browser and API share one origin through the proxy.

Install dependencies with `npm install` and `python3 -m pip install -r requirements.txt`.

## Database

PyAssist uses the existing SQLite database at `./pyassist.db` by default. It intentionally ignores Replit's injected PostgreSQL `DATABASE_URL` so starting the app does not switch databases or strand existing SQLite data. An intentional database override must use `PYASSIST_DATABASE_URL`.

## Gemini

Set `GEMINI_API_KEY` in Replit Secrets to enable real Gemini responses for Ask, Generate, Debug, Explain, and Review. The key is read by the backend only. Without it, Ask mode uses the local Python knowledge base; the other four modes report that Gemini is unavailable rather than presenting a knowledge-base answer as generated code or a review.

The configured default model is `gemini-3.1-flash-lite`. It appears in Google's current stable Gemini API model list, but a live request still requires a valid API key and project access.
