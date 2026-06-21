"""
DocuBot API — FastAPI backend with RAG, PDF upload, and conversation memory.

Run:  uvicorn main:app --reload
Docs: http://localhost:8000/docs
"""

import os
import json
import shutil
import sqlite3
from datetime import datetime
from contextlib import asynccontextmanager

import chromadb
import anthropic
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from pdf_parser import process_pdf
from models import DocumentAnswer, extract_json_from_markdown, DOCUMENT_QA_SYSTEM_PROMPT

load_dotenv()

CHROMA_PERSIST_DIR = "./chroma_data"
UPLOAD_DIR = "./uploads"
DB_PATH = "conversations.db"


# ---------------------------------------------------------------------------
# Database helpers (conversation memory)
# ---------------------------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.commit()
    conn.close()


def save_message(conversation_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.now()
    cur.execute(
        "INSERT OR IGNORE INTO conversations (id, created_at, updated_at) VALUES (?, ?, ?)",
        (conversation_id, now, now),
    )
    cur.execute(
        "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, now),
    )
    cur.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
    conn.commit()
    conn.close()


def load_conversation(conversation_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp",
        (conversation_id,),
    )
    messages = [{"role": row[0], "content": row[1]} for row in cur.fetchall()]
    conn.close()
    return messages


# ---------------------------------------------------------------------------
# Lifespan — initialise resources on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    init_db()
    app.state.chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    app.state.claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    yield


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="DocuBot API",
    description="AI-powered document assistant with RAG",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later.", "limit": str(exc.detail)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    user_id: str
    conversation_id: str
    question: str
    collection_name: str = "docubot"


class ChatResponse(BaseModel):
    conversation_id: str
    user_question: str
    answer: str | None = None
    reasoning: str | None = None
    confidence: str | None = None
    section_referenced: str | None = None
    sources: list[str] = []
    status: str


class UploadResponse(BaseModel):
    status: str
    filename: str
    chunks_ingested: int
    collection_name: str


class HealthResponse(BaseModel):
    status: str
    message: str
    collections: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health_check():
    chroma: chromadb.ClientAPI = app.state.chroma
    collections = chroma.list_collections()
    return {
        "status": "ok",
        "message": "DocuBot API is running",
        "collections": len(collections),
    }


@app.post("/upload", response_model=UploadResponse)
@limiter.limit("5/hour")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    collection_name: str = Form("docubot"),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks, _ = process_pdf(save_path)

    chroma: chromadb.ClientAPI = app.state.chroma
    collection = chroma.get_or_create_collection(name=collection_name)

    existing = collection.count()
    ids = [f"chunk_{existing + i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [{"page": c["page"], "length": c["length"], "source": file.filename} for c in chunks]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_ingested": len(chunks),
        "collection_name": collection_name,
    }


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/hour")
async def chat(request: Request, request_body: ChatRequest):
    chroma: chromadb.ClientAPI = app.state.chroma
    claude: anthropic.Anthropic = app.state.claude

    try:
        collection = chroma.get_collection(name=request_body.collection_name)
    except Exception:
        collection = None

    context = ""
    if collection and collection.count() > 0:
        results = collection.query(query_texts=[request_body.question], n_results=min(3, collection.count()))
        context = "\n\n".join(results["documents"][0])

    history = load_conversation(request_body.conversation_id)

    if context:
        user_content = f"Document context:\n{context}\n\nUser question: {request_body.question}"
    else:
        user_content = request_body.question

    history.append({"role": "user", "content": user_content})
    save_message(request_body.conversation_id, "user", user_content)

    try:
        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            temperature=0.2,
            system=DOCUMENT_QA_SYSTEM_PROMPT if context else "You are a helpful document assistant. Answer questions clearly and concisely.",
            messages=history,
        )

        response_text = response.content[0].text
        save_message(request_body.conversation_id, "assistant", response_text)

        if context:
            clean_json = extract_json_from_markdown(response_text)
            try:
                parsed = DocumentAnswer(**json.loads(clean_json))
                return ChatResponse(
                    conversation_id=request_body.conversation_id,
                    user_question=request_body.question,
                    answer=parsed.answer,
                    reasoning=parsed.reasoning,
                    confidence=parsed.confidence,
                    section_referenced=parsed.section_referenced,
                    sources=parsed.sources,
                    status="success",
                )
            except (json.JSONDecodeError, ValueError):
                pass

        return ChatResponse(
            conversation_id=request_body.conversation_id,
            user_question=request_body.question,
            answer=response_text,
            status="success",
        )

    except Exception as e:
        return ChatResponse(
            conversation_id=request_body.conversation_id,
            user_question=request_body.question,
            answer=str(e),
            status="error",
        )


@app.get("/collections")
async def list_collections():
    chroma: chromadb.ClientAPI = app.state.chroma
    collections = chroma.list_collections()
    result = []
    for col in collections:
        result.append({"name": col.name, "count": col.count()})
    return {"collections": result}


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    messages = load_conversation(conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "conversation_id": conversation_id,
        "message_count": len(messages),
        "messages": messages,
    }


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    cur.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    deleted = conn.total_changes
    conn.commit()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted", "conversation_id": conversation_id}


@app.get("/")
async def root():
    return {
        "name": "DocuBot API",
        "version": "2.0.0",
        "docs": "http://localhost:8000/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
