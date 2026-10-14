# PyAssist — Personal Python Question-Answering Chatbot

A production-grade, internship-level full-stack mini-project featuring a natural-language Python programming Q&A chatbot powered by a deterministic, transparent knowledge retrieval engine, persistent SQLite database with SQLAlchemy ORM, robust Argon2 authentication, session-based CSRF protection, and a modern developer-tool UI.

---

## 🌟 Key Features

1. **Deterministic Python Knowledge Base (30+ Topics)**:
   - Covers core Python syntax, data types, operators, conditionals, `for` and `while` loops, functions, `*args`/`**kwargs`, lambda expressions, list comprehensions, OOP (classes, `__init__`, `self`, inheritance), exception handling (`try`/`except`/`finally`), file I/O (`with open`), modules, packages, decorators, `==` vs `=`, `is` vs `==`, mutability, and common beginner errors.
   - Explanations include formatted overviews, copyable idiomatic Python code blocks, and expected console outputs.
   - Transparent relevance scoring with tokenization, stemming, compound operator protection (`==` vs `=`), keyword weighting, and confidence thresholding.
   - Explicit unsupported-question handling with intelligent related topic suggestions without hallucination or fabrication.

2. **Full Authentication & Security**:
   - Argon2id password hashing (`argon2-cffi`).
   - Cryptographically random session tokens (32 bytes) stored as SHA-256 hashes in SQLite.
   - `HttpOnly`, `SameSite=Lax` session cookies with configurable `Secure` flag for HTTPS.
   - CSRF protection via double-submit / header verification (`X-CSRF-Token`) for state-changing requests.
   - In-memory sliding-window rate limiting on login, registration, and chat endpoints.
   - Parameterized queries via SQLAlchemy preventing SQL injection.
   - Strict user ownership verification on all conversation access and deletion (IDOR prevention).

3. **Developer-Tool UI/UX**:
   - Modern, focused design inspired by VS Code and Linear with violet accent (`#8b5cf6`).
   - Complete Light and Dark themes via CSS custom properties with instant `localStorage` persistence and zero-flash initialization.
   - Collapsible responsive sidebar for mobile devices.
   - 1-Click "Copy Code" and "Copy Answer" actions with visual feedback.
   - Quick-question clickable chips and interactive Topics Explorer modal.
   - Real-time character counter and auto-resizing input textarea (Enter to send, Shift+Enter for newline).

---

## 🏗️ Architecture

```
pyassist/
├── app/
│   ├── __init__.py           # Application package metadata
│   ├── main.py               # FastAPI application, static mounting & health route
│   ├── config.py             # Settings, environment variables, security defaults
│   ├── database.py           # SQLAlchemy engine, session maker, DB initialization
│   ├── models.py             # ORM models (User, UserSession, Conversation, Message)
│   ├── schemas.py            # Pydantic v2 validation models
│   ├── auth.py               # Argon2 hashing, token generation, CSRF, rate limiter
│   ├── knowledge_base.py     # 30+ structured Python topics, examples, outputs
│   ├── chatbot.py            # Normalized text retrieval engine & transparent scoring
│   └── routes/
│       ├── __init__.py
│       ├── authentication.py # /api/auth (register, login, logout, me, csrf)
│       ├── chat.py           # /api/chat (ask, topics)
│       └── history.py        # /api/history (list, detail, delete)
├── static/
│   ├── index.html            # Main chat interface
│   ├── login.html            # Sign in page
│   ├── register.html         # Sign up page
│   ├── css/
│   │   └── style.css         # Theme tokens, layout, mobile responsive rules
│   └── js/
│       ├── app.js            # Main chat client, DOM rendering, history sync
│       └── auth.js           # Auth forms, validation, CSRF, demo filler
├── tests/
│   ├── conftest.py           # Isolated test database and TestClient fixtures
│   ├── test_auth.py          # Registration, login, validation, logout tests
│   ├── test_chat.py          # Known Qs, phrasings, unsupported, topics & regression tests
│   ├── test_history.py       # Persistence, retrieval, deletion, isolation tests
│   └── test_security.py      # Cookie attributes, CSRF enforcement, XSS defense
├── .env.example              # Template environment configuration
├── .gitignore                # Git exclusions (DBs, caches, venv, secrets)
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dev scripts & types
├── server.ts                 # Dev server gateway proxy
└── README.md                 # Project documentation
```

---

## ▶️ Run on Replit

Install the dependencies once, then start the Node gateway and FastAPI service together:

```bash
npm install
python3 -m pip install -r requirements.txt
npm run dev
```

The gateway listens on port 5000 by default and proxies same-origin requests to FastAPI on port 8888. Set `GEMINI_API_KEY` in Replit Secrets to enable real Gemini answers for all five modes. Without that secret, Ask mode uses the local knowledge base and the other modes clearly report that Gemini is unavailable.

PyAssist uses SQLite at `./pyassist.db` by default and does not consume Replit's injected PostgreSQL `DATABASE_URL`. To intentionally select a different database, set `PYASSIST_DATABASE_URL`.

---

## 🚀 Local Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.10 & 3.11)
- `pip` package manager

### Option A: Windows PowerShell Setup

```powershell
# 1. Clone or navigate to the project directory
cd pyassist

# 2. Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy environment configuration
Copy-Item .env.example .env

# 5. Start the FastAPI server
uvicorn pyassist.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at `http://127.0.0.1:8000`.

---

### Option B: Linux / macOS Bash Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Start application
uvicorn pyassist.app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## ⚡ Demo User Credentials

The application automatically seeds a default demo user upon first database initialization:
- **Username**: `demo_user`
- **Password**: `Password123`
- **Email**: `demo@pyassist.dev`

On the login page, you can also click the **"⚡ Fill Demo Credentials"** button for instant sign-in.

---

## 🧪 Running Automated Tests

PyAssist comes with a comprehensive test suite of 23 tests covering authentication, knowledge retrieval, history isolation, CSRF protection, cookie security, and regression edge cases.

```bash
# Run all tests with pytest
python3 -m pytest tests -v
```

All tests execute against an isolated SQLite test database and clean up automatically.

---

## 📡 API Reference

### Authentication (`/api/auth`)
- `POST /api/auth/register` — Register a new account (`username`, `email`, `password`). Issues HttpOnly session cookie.
- `POST /api/auth/login` — Sign in with `username_or_email` and `password`.
- `POST /api/auth/logout` — Revoke active session in database and delete cookies (requires CSRF token).
- `GET /api/auth/me` — Return current authenticated user profile (`id`, `username`, `email`, `created_at`).
- `GET /api/auth/csrf` — Obtain initial CSRF token for state-changing requests.

### Chat & Knowledge Retrieval (`/api/chat`)
- `POST /api/chat/ask` — Submit natural-language question. Returns answer, code snippet, expected output, related topics, and confidence score.
- `GET /api/chat/topics` — List all 30+ supported knowledge base topics and summaries.

### Conversation History (`/api/history`)
- `GET /api/history` — List all conversations for the authenticated user with preview and timestamps.
- `GET /api/history/{conversation_id}` — Retrieve full message history (strict ownership verified).
- `DELETE /api/history/{conversation_id}` — Permanently delete a conversation (strict ownership verified, requires CSRF token).

### System (`/api/health`)
- `GET /api/health` — Return service and database status without exposing internal paths or credentials.

---

## 🔒 Security Design

- **Argon2 Hashing**: Uses `argon2-cffi` with modern salt parameters. Plaintext passwords are never logged or stored.
- **Session Tokens**: Server generates 32 bytes of cryptographically secure random bytes via `secrets.token_urlsafe(32)`. Only the SHA-256 hash is persisted in the database.
- **CSRF Defense**: State-changing endpoints require matching `X-CSRF-Token` headers.
- **Access Control (IDOR Prevention)**: All queries to `conversations` filter by `user_id == current_user.id`. A user cannot read or delete another user's conversations.
- **Anti-XSS**: Frontend uses standard DOM creation and `textContent` for user inputs and code blocks; no raw `innerHTML` injection of unescaped user messages.
- **Strict Separation**: User questions are treated strictly as data queries and are never executed via Python `exec()` or `eval()`.
