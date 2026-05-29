from pathlib import Path
import json
import re
from typing import List, Dict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.backend.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[3]

RULES_DIR = PROJECT_ROOT / "data" / "inspection_rules"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"

FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index.bin"
CHUNKS_PATH = VECTOR_STORE_DIR / "rule_chunks.json"


class RAGService:
    """
    Retrieval service for industrial inspection rules.

    Responsibilities:
    - Load inspection rule markdown files
    - Split them into rule chunks
    - Generate embeddings
    - Build and save FAISS index
    - Retrieve relevant rules for a query
    """

    def __init__(self):
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.index = None
        self.rule_chunks = []

    def load_rule_documents(self) -> List[Dict]:
        if not RULES_DIR.exists():
            raise FileNotFoundError(f"Rules directory not found: {RULES_DIR}")

        documents = []

        for file_path in RULES_DIR.glob("*.md"):
            content = file_path.read_text(encoding="utf-8")

            documents.append({
                "filename": file_path.name,
                "content": content
            })

        if not documents:
            raise ValueError("No rule documents found.")

        return documents

    def extract_rule_chunks(self, documents: List[Dict]) -> List[Dict]:
        chunks = []

        for doc in documents:
            filename = doc["filename"]
            content = doc["content"]

            raw_rules = re.split(r"(?=## Rule ID:)", content)

            for raw_rule in raw_rules:
                raw_rule = raw_rule.strip()

                if not raw_rule.startswith("## Rule ID:"):
                    continue

                rule_id_match = re.search(r"Rule ID:\s*([A-Z]+-\d+)", raw_rule)
                category_match = re.search(r"Category:\s*(.*)", raw_rule)
                severity_match = re.search(r"Severity:\s*(.*)", raw_rule)

                rule_id = rule_id_match.group(1).strip() if rule_id_match else "UNKNOWN"
                category = category_match.group(1).strip() if category_match else "Unknown"
                severity = severity_match.group(1).strip() if severity_match else "Unknown"

                chunks.append({
                    "rule_id": rule_id,
                    "category": category,
                    "severity": severity,
                    "source_file": filename,
                    "text": raw_rule
                })

        if not chunks:
            raise ValueError("No rule chunks extracted. Check markdown formatting.")

        return chunks

    def build_vector_store(self) -> Dict:
        VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

        documents = self.load_rule_documents()
        self.rule_chunks = self.extract_rule_chunks(documents)

        rule_texts = [chunk["text"] for chunk in self.rule_chunks]

        embeddings = self.embedding_model.encode(
            rule_texts,
            convert_to_numpy=True,
            show_progress_bar=True
        ).astype("float32")

        faiss.normalize_L2(embeddings)

        embedding_dim = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(embedding_dim)
        self.index.add(embeddings)

        faiss.write_index(self.index, str(FAISS_INDEX_PATH))

        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.rule_chunks, f, indent=4, ensure_ascii=False)

        return {
            "status": "success",
            "rule_count": len(self.rule_chunks),
            "embedding_model": self.embedding_model_name,
            "faiss_index_path": str(FAISS_INDEX_PATH),
            "chunks_path": str(CHUNKS_PATH)
        }

    def load_vector_store(self) -> None:
        if not FAISS_INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {FAISS_INDEX_PATH}. "
                "Run build_vector_store() first."
            )

        if not CHUNKS_PATH.exists():
            raise FileNotFoundError(
                f"Rule chunks not found: {CHUNKS_PATH}. "
                "Run build_vector_store() first."
            )

        self.index = faiss.read_index(str(FAISS_INDEX_PATH))

        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            self.rule_chunks = json.load(f)

    def retrieve_rules(self, query: str, top_k: int | None = None) -> List[Dict]:
        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        if self.index is None or not self.rule_chunks:
            self.load_vector_store()

        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).astype("float32")

        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            chunk = self.rule_chunks[idx].copy()
            chunk["score"] = float(score)
            results.append(chunk)

        return results


if __name__ == "__main__":
    rag_service = RAGService()

    print("Building vector store...")
    build_result = rag_service.build_vector_store()
    print(build_result)

    test_query = "worker missing helmet near operating machinery"
    print("\nTest query:", test_query)

    results = rag_service.retrieve_rules(test_query, top_k=3)

    for result in results:
        print("\n---")
        print("Score:", round(result["score"], 4))
        print("Rule ID:", result["rule_id"])
        print("Category:", result["category"])
        print("Severity:", result["severity"])
        print("Source:", result["source_file"])