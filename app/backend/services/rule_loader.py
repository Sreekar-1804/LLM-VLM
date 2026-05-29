from pathlib import Path


RULES_DIR = Path("data/inspection_rules")


def load_rule_documents() -> list[dict]:
    """
    Loads all markdown rule files from the inspection_rules directory.
    Returns a list of dictionaries with filename and content.
    """

    if not RULES_DIR.exists():
        raise FileNotFoundError(f"Rules directory not found: {RULES_DIR}")

    documents = []

    for file_path in RULES_DIR.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "filename": file_path.name,
                "content": content
            }
        )

    if not documents:
        raise ValueError("No rule documents found.")

    return documents


if __name__ == "__main__":
    docs = load_rule_documents()

    print(f"Loaded {len(docs)} rule documents:\n")

    for doc in docs:
        print(f"- {doc['filename']} | {len(doc['content'])} characters")