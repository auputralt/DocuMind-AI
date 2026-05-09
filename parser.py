import fitz  # PyMuPDF
from docx import Document
import io
import tiktoken
from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Chunks text into overlapping segments based on token count."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Fallback if tiktoken fails
        encoding = tiktoken.encoding_for_model("gpt-4o")
        
    tokens = encoding.encode(text)
    chunks = []
    
    if not tokens:
        return chunks
        
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        if i + chunk_size >= len(tokens):
            break
            
    return chunks

def parse_document(file_content: bytes, file_name: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    Extracts text from various document formats and returns overlapping chunks
    along with their metadata.
    """
    file_extension = file_name.split('.')[-1].lower()
    text = ""
    
    try:
        if file_extension == 'pdf':
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                text = "\n".join(page.get_text() for page in doc)
                
        elif file_extension in ['doc', 'docx']:
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            
        elif file_extension in ['txt', 'csv']:
            text = file_content.decode('utf-8', errors='ignore')
            
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
    except Exception as e:
        raise RuntimeError(f"Error parsing {file_name}: {str(e)}")

    # Chunk the extracted text
    raw_chunks = chunk_text(text, chunk_size, overlap)
    
    # Package into structured chunks with metadata
    structured_chunks = []
    for i, chunk in enumerate(raw_chunks):
        structured_chunks.append({
            "text": chunk,
            "metadata": {
                "source": file_name,
                "chunk_index": i
            }
        })
        
    return structured_chunks
