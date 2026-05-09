from embedder import get_chroma_client, COLLECTION_NAME
from typing import List, Dict

def retrieve_context(query: str, top_k: int = 5, **kwargs) -> List[Dict]:
    client = get_chroma_client()

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    if not results or not results['documents'] or not results['documents'][0]:
        return []

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]

    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(documents, metadatas)
    ]
