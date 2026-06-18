from pypdf import PdfReader
import re

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    metadata = {}
    
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
    
    metadata['total_pages'] = len(reader.pages)
    
    return text, metadata

def chunk_text_with_metadata(text, chunk_size=1000, overlap=200):
    """Split text into chunks with page metadata."""
    chunks = []
    sentences = text.split('. ')
    
    current_chunk = ""
    current_page = 1
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Extract page number if present
        match = re.search(r'--- Page (\d+) ---', sentence)
        if match:
            current_page = int(match.group(1))
            continue
        
        if not sentence.endswith('.'):
            sentence += '.'
        
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "page": current_page,
                "length": len(current_chunk)
            })
            current_chunk = current_chunk[-overlap:] + " " + sentence
        else:
            current_chunk += " " + sentence
    
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "page": current_page,
            "length": len(current_chunk)
        })
    
    return chunks

def process_pdf(pdf_path, chunk_size=1000, overlap=200):
    """End-to-end: PDF file → list of chunks with metadata."""
    text, metadata = extract_text_from_pdf(pdf_path)
    chunks = chunk_text_with_metadata(text, chunk_size, overlap)
    return chunks, metadata

if __name__ == "__main__":
    pdf_path = "sample_policy.pdf"
    chunks, meta = process_pdf(pdf_path)
    
    print(f"Extracted {meta['total_pages']} pages into {len(chunks)} chunks\n")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1} (Page {chunk['page']}, {chunk['length']} chars)")
        print(f"Text: {chunk['text'][:150]}...\n")