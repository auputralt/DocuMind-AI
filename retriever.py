import re
from typing import List, Dict
from embedder import load_all_chunks


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


def retrieve_context(query: str, top_k: int = 5, **kwargs) -> List[Dict]:
    all_chunks = load_all_chunks()
    if not all_chunks:
        return []

    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    scored = []
    for chunk in all_chunks:
        chunk_tokens = set(_tokenize(chunk["text"]))
        overlap = len(query_tokens & chunk_tokens)
        if overlap > 0:
            scored.append((overlap, chunk))

    if not scored:
        return []

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
