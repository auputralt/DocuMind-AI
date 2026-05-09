import json
import os
from typing import List, Dict

CHUNKS_PATH = os.environ.get("CHUNKS_PATH", ".doc_chunks.json")


def store_chunks(chunks: List[Dict]):
    if not chunks:
        return

    all_chunks = _load_all()

    source = chunks[0]["metadata"]["source"]
    all_chunks = [c for c in all_chunks if c["metadata"]["source"] != source]
    all_chunks.extend(chunks)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False)


def load_all_chunks() -> List[Dict]:
    return _load_all()


def clear_database():
    if os.path.exists(CHUNKS_PATH):
        os.remove(CHUNKS_PATH)


def _load_all() -> List[Dict]:
    if not os.path.exists(CHUNKS_PATH):
        return []
    try:
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
