import os
from pathlib import Path
from typing import Optional
from openai import OpenAI


class KnowledgeBase:
    """Simple knowledge base that loads documents and retrieves relevant context.

    Uses OpenAI embeddings + simple cosine similarity for retrieval.
    No external vector DB needed - runs in-memory for the demo.
    """

    def __init__(self, kb_dir: str = None):
        self.client = OpenAI() if os.getenv("OPENAI_API_KEY") else None
        self.kb_dir = kb_dir or str(Path(__file__).resolve().parent.parent / "knowledge_base")
        self.documents: list[dict] = []
        self._load_documents()

    def _load_documents(self):
        kb_path = Path(self.kb_dir)
        if not kb_path.exists():
            return

        for file_path in kb_path.glob("*.txt"):
            category = file_path.stem
            content = file_path.read_text().strip()
            chunks = self._chunk_text(content, category)
            self.documents.extend(chunks)

    def _chunk_text(self, text: str, category: str, chunk_size: int = 500) -> list[dict]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i : i + chunk_size]
            chunks.append({
                "category": category,
                "content": " ".join(chunk_words),
                "index": len(chunks),
            })
        return chunks

    def _get_embedding(self, text: str) -> list[float]:
        if not self.client:
            return []
        try:
            resp = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return resp.data[0].embedding
        except Exception:
            return []

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if not norm_a or not norm_b:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(self, query: str, category: str = None, top_k: int = 2) -> list[str]:
        if not self.client or not self.documents:
            return []

        query_emb = self._get_embedding(query)
        if not query_emb:
            return []

        scored = []
        for doc in self.documents:
            if category and doc["category"] != category:
                continue
            doc_emb = self._get_embedding(doc["content"])
            score = self._cosine_similarity(query_emb, doc_emb)
            scored.append((score, doc["content"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [content for _, content in scored[:top_k]]

    def get_context(self, query: str, category: str = None) -> str:
        results = self.search(query, category)
        if not results:
            return ""
        return "\n\n---\n\n".join(results)
