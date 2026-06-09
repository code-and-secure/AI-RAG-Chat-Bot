# Vaultix — AI RAG Chat Bot

An intelligent document chat application powered by Retrieval-Augmented Generation (RAG). Upload any document and instantly chat with your private data. When the document doesn't contain an answer, Vaultix automatically searches the web for you.

**Stack:** React + Vite + Tailwind CSS (frontend) · FastAPI + LangChain + ChromaDB (backend) · Groq LLM (qwen3-32b) · HuggingFace Embeddings

---

## Features

- **Document Chat** — Upload PDF, TXT, or DOCX and ask questions about its content
- **Web Fallback** — Automatically searches the web when your document doesn't have the answer
- **Public Bots** — Pre-configured bots for Finance, HR Policy, and Legal (NDA) domains
- **Web Scraper** — Enter any URL to scrape, index, and chat about it
- **Light / Dark Mode** — Persistent theme toggle
- **Wandering Bot** — Animated avatar that reacts to app state

---

## Prerequisites

Make sure the following are installed on your machine:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.10+ | https://python.org |
| Node.js | 18+ (LTS) | https://nodejs.org |
| Git | Any | https://git-scm.com |

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd AI-RAG-Chat-Bot
```

### 2. Create and activate a Python virtual environment

```bash
python -m venv venv

# Windows (Git Bash / PowerShell)
source venv/Scripts/activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

> The first run will download the `sentence-transformers/all-MiniLM-L6-v2` model (~90 MB). This is cached locally and only happens once.

### 4. Configure environment variables

The `.env` file inside `backend/` already contains the default Groq API key for development:

```
backend/.env
```

```env
GROQ_API_KEY=your_groq_api_key_here
HF_HUB_DISABLE_SYMLINKS_WARNING=1
```

To get your own Groq API key: https://console.groq.com

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

> Only needs to be run once.

---

## Running the Project

Start both the backend and frontend with a single command from the project root:

```bash
python dev.py
```

| Service | URL |
|---------|-----|
| Frontend (React) | http://localhost:5173 |
| Backend (FastAPI) | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

Press `Ctrl+C` to stop both servers.

---

## Project Structure

```
AI-RAG-Chat-Bot/
├── backend/
│   ├── main.py            # FastAPI app — all API endpoints
│   ├── rag.py             # Document processing & vector store logic
│   ├── search.py          # Web search & scraping (Google, DuckDuckGo, Wikipedia)
│   ├── requirements.txt   # Python dependencies
│   └── .env               # API keys (Groq)
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                     # Root component + theme management
│   │   ├── api.ts                      # API client (fetch wrappers)
│   │   ├── types.ts                    # Shared TypeScript types
│   │   ├── components/
│   │   │   ├── Sidebar.tsx             # Navigation + theme toggle
│   │   │   └── WanderingBot.tsx        # Animated bot avatar
│   │   └── pages/
│   │       ├── ChatPage.tsx            # Document upload + chat interface
│   │       ├── MyBotsPage.tsx          # Active bot + statistics
│   │       ├── PublicBotsPage.tsx      # Pre-configured domain bots
│   │       └── IntegrationsPage.tsx    # Web scraper + Slack + Notion
│   ├── public/
│   │   └── robot.png                  # Bot avatar image
│   ├── package.json
│   ├── vite.config.ts                 # Vite config (proxies /api → :8000)
│   └── tailwind.config.js
│
├── dev.py                 # Single-command dev server launcher
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a document (PDF/TXT/DOCX) |
| `POST` | `/api/chat` | Send a query against a session |
| `POST` | `/api/scrape` | Scrape a URL and build a session |
| `POST` | `/api/public-bot/{type}` | Activate a pre-configured bot (`finance`, `hr`, `legal`) |
| `GET` | `/api/stats` | Get usage statistics |
| `DELETE` | `/api/session/{id}` | Clear a session from memory |

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'langchain_huggingface'`**
```bash
pip install langchain-huggingface
```

**`FileNotFoundError` when running `python dev.py` (npm not found)**
Make sure Node.js is installed and accessible. Run `node --version` to verify.

**Backend starts but frontend shows blank page**
Make sure you ran `npm install` inside the `frontend/` folder at least once.

**Port already in use**
Kill the process using the port and restart:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```
