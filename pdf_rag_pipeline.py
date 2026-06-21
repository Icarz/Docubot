import chromadb
import anthropic
import json
from sentence_transformers import SentenceTransformer
from pdf_parser import process_pdf
from models import DocumentAnswer, extract_json_from_markdown, DOCUMENT_QA_SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = "./chroma_data"
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def ingest_pdf(pdf_path, collection_name="docubot"):
    """
    Parse PDF, embed chunks, store in ChromaDB.
    """
    print(f"\nIngesting {pdf_path}...")
    
    # Parse PDF into chunks
    chunks, metadata = process_pdf(pdf_path)
    
    # Get or create collection
    collection = client.get_or_create_collection(name=collection_name)
    
    # Process each chunk
    ids = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        # Generate unique ID
        chunk_id = f"chunk_{i}"
        ids.append(chunk_id)
        
        # Store chunk text
        documents.append(chunk["text"])
        
        # Store metadata (page number)
        metadatas.append({"page": chunk["page"], "length": chunk["length"]})
    
    # Add to ChromaDB (embeddings are created automatically)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    print(f"✓ Ingested {len(chunks)} chunks from {pdf_path}")
    print(f"✓ Stored in collection: {collection_name}")
    print(f"✓ Collection now has {collection.count()} documents")
    return collection

def query_collection(query, collection_name="docubot", top_k=3):
    """
    Embed a question and retrieve the most similar chunks.
    """
    # Get collection
    collection = client.get_collection(name=collection_name)
    
    # Query returns top-k most similar chunks
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Format results
    retrieved_chunks = []
    for i in range(len(results['ids'][0])):
        chunk = {
            "id": results['ids'][0][i],
            "text": results['documents'][0][i],
            "page": results['metadatas'][0][i]['page'],
            "distance": results['distances'][0][i]  # Lower = more similar
        }
        retrieved_chunks.append(chunk)
    
    return retrieved_chunks

def rag_query(question, collection_name="docubot", top_k=3):
    """
    Complete RAG: retrieve chunks → inject into Claude → get answer.
    """
    # Step 1: Retrieve relevant chunks
    retrieved_chunks = query_collection(question, collection_name, top_k)
    
    # Step 2: Build context from retrieved chunks
    context = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])
    
    # Step 3: Call Claude with context
    claude_client = anthropic.Anthropic()
    
    system_prompt = DOCUMENT_QA_SYSTEM_PROMPT
    
    user_message = f"""Document context:
{context}

User question: {question}"""
    
    response = claude_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    # Step 4: Parse Claude's response
    response_text = response.content[0].text
    clean_json = extract_json_from_markdown(response_text)
    
    try:
        answer_data = json.loads(clean_json)
        answer = DocumentAnswer(**answer_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing response: {e}")
        answer = None
    
    return answer, retrieved_chunks

def print_results(question, answer, chunks):
    """Pretty print RAG results."""
    print(f"\n{'='*60}")
    print(f"QUESTION: {question}")
    print(f"{'='*60}\n")
    
    print(f"Retrieved {len(chunks)} relevant chunks:")
    for i, chunk in enumerate(chunks):
        print(f"  {i+1}. Page {chunk['page']} (distance: {chunk['distance']:.3f})")
        print(f"     {chunk['text'][:100]}...\n")
    
    print(f"{'='*60}")
    print(f"ANSWER")
    print(f"{'='*60}")
    if answer:
        print(f"Reasoning: {answer.reasoning}\n")
        print(f"Answer: {answer.answer}\n")
        print(f"Confidence: {answer.confidence}")
        print(f"Section: {answer.section_referenced}")
        print(f"Sources: {', '.join(answer.sources)}")
    else:
        print("Failed to get answer")
    print(f"{'='*60}\n")

# Main execution
if __name__ == "__main__":
    # Step 1: Ingest PDF
    collection = ingest_pdf("sample_policy.pdf")
    
    # Step 2: Test queries
    test_questions = [
        "What is the refund window?",
        "Can I return an item after 31 days?",
        "Do I have to pay for return shipping?"
    ]
    
    for question in test_questions:
        answer, chunks = rag_query(question)
        print_results(question, answer, chunks)