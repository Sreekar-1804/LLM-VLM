from app.backend.services.rag_service import RAGService


def test_rag_retrieves_rules():
    rag_service = RAGService()

    results = rag_service.retrieve_rules(
        query="worker missing helmet near machine",
        top_k=3
    )

    assert len(results) > 0
    assert "rule_id" in results[0]
    assert "text" in results[0]
    assert "score" in results[0]


def test_rag_retrieves_defect_rules():
    rag_service = RAGService()

    results = rag_service.retrieve_rules(
        query="metal component has visible surface crack",
        top_k=3
    )

    rule_ids = [result["rule_id"] for result in results]

    assert len(results) > 0
    assert any(rule_id.startswith("DEF") for rule_id in rule_ids)


def test_rag_top_k_limit():
    rag_service = RAGService()

    results = rag_service.retrieve_rules(
        query="blocked emergency exit",
        top_k=2
    )

    assert len(results) <= 2