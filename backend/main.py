import os
import re
import json
import uuid
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from rag import process_file_bytes, build_from_texts, build_from_scraped
from search import google_search_context, fetch_page_text

load_dotenv()

app = FastAPI(title="DocuMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> {docs, db, retriever, name}
sessions: dict[str, dict] = {}

STATS_FILE = "stats.json"

PUBLIC_BOTS = {
    "finance": {
        "name": "FinanceAI",
        "texts": [
            "Tesla Q4 2025 Financial Summary: Total revenues grew 14% year-over-year to $25.5 Billion. GAAP operating margin stood at 18.2%. Cybertruck deliveries reached an all-time high of 150,000 units.",
            "Tesla cash and cash equivalents grew by $2.3B to $28.1B at the end of fiscal year 2025. Energy generation and storage revenue hit a record $2.1B.",
        ],
        "source": "Tesla_Q4_2025.pdf",
    },
    "hr": {
        "name": "HR Advisor",
        "texts": [
            "Employee Benefits Policy: Standard Paid Time Off (PTO) is 20 days per calendar year. Healthcare insurance premium is 100% covered by the company for full-time employees.",
            "Remote Work Policy: Standard remote working hours are 9:00 AM to 6:00 PM. Employees are requested to core collaborate between 11:00 AM and 3:00 PM.",
        ],
        "source": "Employee_Handbook_2026.pdf",
    },
    "legal": {
        "name": "Legal Advisor",
        "texts": [
            "Non-Disclosure Agreement: The term of this Agreement shall be 3 years from the Effective Date. The receiving party agrees to safeguard all proprietary confidential data.",
            "Governing Law: This NDA and all conflicts arising hereunder shall be strictly governed by and construed in accordance with the laws of the State of Delaware.",
        ],
        "source": "Standard_NDA_Template.pdf",
    },
}


def load_stats() -> dict:
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_queries": 0, "total_docs": 0, "total_bots": 0}


def update_stat(key: str, increment: int = 1):
    stats = load_stats()
    stats[key] = stats.get(key, 0) + increment
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")
    return ChatGroq(model="qwen/qwen3-32b", temperature=0.3)


def clean_response(text: str) -> str:
    """Strip Qwen3 <think>...</think> reasoning blocks from output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# ── Upload ──────────────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".pdf", ".txt", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF, TXT, DOCX supported")

    content = await file.read()
    docs, db, retriever = process_file_bytes(content, file.filename)

    session_id = str(uuid.uuid4())
    sessions[session_id] = {"docs": docs, "db": db, "retriever": retriever, "name": file.filename}

    update_stat("total_docs", 1)
    update_stat("total_bots", 1)

    return {"session_id": session_id, "filename": file.filename, "chunks": len(docs)}


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    llm = get_llm()
    normalized = req.query.strip().lower()

    relevant_docs = []
    best_score = 0.0
    session = sessions.get(req.session_id) if req.session_id else None

    if session:
        db = session["db"]
        retriever = session["retriever"]
        try:
            scored = db.similarity_search_with_relevance_scores(normalized, k=4)
            if scored:
                best_score = scored[0][1]
                relevant_docs = [d for d, _ in scored[:5]]
        except Exception:
            pass
        if not relevant_docs:
            relevant_docs = retriever.invoke(normalized)

    context = "\n\n".join([d.page_content for d in relevant_docs])

    prompt = f"""Answer the question using ONLY the context below. Be direct and concise — no preamble, no filler phrases.
If the context does not contain the answer, reply with exactly: "NOT_IN_DOC"

Context:
{context}

Question: {req.query}

Answer:"""

    used_web = False
    final_answer = ""

    should_fallback = not relevant_docs or best_score < 0.08
    if not should_fallback:
        raw = llm.invoke(prompt)
        final_answer = clean_response(raw.content)
        if "NOT_IN_DOC" in final_answer or not final_answer:
            should_fallback = True

    if should_fallback:
        used_web = True
        web_context, _ = google_search_context(req.query, num_results=3)
        if web_context:
            web_prompt = f"""Answer the question below accurately and concisely using the web context provided.
- Give a clear, informative answer (2-4 sentences or a short list if needed).
- Do not say "based on the context" or repeat the question.
- End with a "Sources:" line listing the URLs.

Web Context:
{web_context}

Question: {req.query}

Answer:"""
            web_raw = llm.invoke(web_prompt)
            final_answer = clean_response(web_raw.content)
        else:
            final_answer = "Could not find an answer in your document or on the web."

    update_stat("total_queries", 1)
    return {"answer": final_answer, "used_web": used_web}


# ── Scrape ───────────────────────────────────────────────────────────────────

class ScrapeRequest(BaseModel):
    url: str


@app.post("/api/scrape")
async def scrape(req: ScrapeRequest):
    text = fetch_page_text(req.url, max_chars=8000)
    if not text:
        raise HTTPException(status_code=422, detail="Failed to scrape the URL. Make sure it is valid and public.")

    docs, db, retriever = build_from_scraped(text, req.url)
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"docs": docs, "db": db, "retriever": retriever, "name": f"Scraped: {req.url}"}

    update_stat("total_docs", 1)
    update_stat("total_bots", 1)

    return {"session_id": session_id, "name": f"Scraped: {req.url}", "chunks": len(docs)}


# ── Public bots ───────────────────────────────────────────────────────────────

@app.post("/api/public-bot/{bot_type}")
async def activate_public_bot(bot_type: str):
    bot = PUBLIC_BOTS.get(bot_type)
    if not bot:
        raise HTTPException(status_code=404, detail="Unknown bot type")

    docs, db, retriever = build_from_texts(bot["texts"], bot["source"])
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"docs": docs, "db": db, "retriever": retriever, "name": f"{bot['name']} (Preloaded)"}

    update_stat("total_bots", 1)

    return {"session_id": session_id, "name": f"{bot['name']} (Preloaded)", "chunks": len(docs)}


# ── Session ───────────────────────────────────────────────────────────────────

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    sessions.pop(session_id, None)
    return {"ok": True}


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
async def get_stats():
    return load_stats()
