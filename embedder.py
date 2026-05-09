import chromadb
import os
from typing import List, Dict

CHROMA_DATA_PATH = os.environ.get("CHROMA_PATH", ".chroma_db")
COLLECTION_NAME = "documind_documents"

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DATA_PATH)

def store_chunks(chunks: List[Dict]):
    if not chunks:
        return

    client = get_chroma_client()
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    source_name = chunks[0]["metadata"]["source"]
    try:
        collection.delete(where={"source": source_name})
    except Exception:
        pass

    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [f"{source_name}_chunk_{c['metadata']['chunk_index']}" for c in chunks]

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

def clear_database():
    client = get_chroma_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
