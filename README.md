# DocuBot

AI-powered document assistant that answers questions grounded in your PDF documents. Built with **Claude API**, **ChromaDB**, and **FastAPI**.

Upload a PDF, ask questions, and get structured answers with reasoning, confidence scores, and source citations — all backed by Retrieval Augmented Generation (RAG).

## How It Works

```
PDF Upload → Parse & Chunk → Embed → Store in ChromaDB
                                          ↓
User Question → Retrieve Similar Chunks → Inject as Context → Claude → Structured JSON Answer
```

1. **Upload** a PDF via `/upload` — it's parsed into overlapping text chunks and stored as vectors in ChromaDB
2. **Ask** a question via `/chat` — the most relevant chunks are retrieved, injected into the prompt, and Claude returns a structured answer
3. **Multi-turn** — conversation history is persisted in SQLite, so follow-up questions work across sessions

## Quick Start

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
# Clone and enter the project
git clone https://github.com/Icarz/docubot.git
cd docubot

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo ANTHROPIC_API_KEY=your-key-here > .env
```

### Run

```bash
uvicorn main:app --reload
```

Server starts at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

## API Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/upload` | Upload a PDF file | 5/hour |
| `POST` | `/chat` | Ask a question (RAG + memory) | 10/hour |
| `GET` | `/collections` | List document collections | - |
| `GET` | `/conversations/{id}` | Load conversation history | - |
| `DELETE` | `/conversations/{id}` | Delete a conversation | - |
| `GET` | `/health` | Server status + collection count | - |

### Upload a PDF

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@sample_policy.pdf" \
  -F "collection_name=docubot"
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "conversation_id": "conv1",
    "question": "What is the refund window?"
  }'
```

**Response:**
```json
{
  "conversation_id": "conv1",
  "user_question": "What is the refund window?",
  "answer": "All purchases are eligible for refund within 30 days of purchase.",
  "reasoning": "Section 3.1 states the refund window is 30 days...",
  "confidence": "high",
  "section_referenced": "Section 3.1: Refund Window",
  "sources": ["All purchases are eligible for refund or return within 30 days of purchase."],
  "status": "success"
}
```

## Project Structure

```
docubot/
├── main.py              # FastAPI backend (RAG + upload + memory + rate limiting)
├── models.py            # Shared Pydantic models and system prompt
├── pdf_parser.py        # PDF text extraction and chunking
├── pdf_rag_pipeline.py  # Standalone RAG pipeline (CLI)
├── eval_prompts.py      # Prompt evaluation suite (4 test cases)
├── create_test_pdf.py   # Generates sample_policy.pdf test fixture
├── sample_policy.pdf    # Test PDF document
├── requirements.txt     # Python dependencies
└── CLAUDE.md            # Claude Code development guide
```

## Tech Stack

- **LLM**: Claude (claude-sonnet-4-6) via Anthropic API
- **Vector DB**: ChromaDB with persistent storage
- **Embeddings**: all-MiniLM-L6-v2 (sentence-transformers)
- **Backend**: FastAPI + Uvicorn
- **Conversation Memory**: SQLite
- **Rate Limiting**: slowapi
- **PDF Parsing**: pypdf
- **Validation**: Pydantic

## Run Evals

```bash
python eval_prompts.py
```

Runs 4 test cases against Claude checking: basic retrieval, hallucination prevention, multi-step reasoning, and citation accuracy.

## License

MIT
