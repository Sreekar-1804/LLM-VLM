from fastapi.testclient import TestClient

from app.backend.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_image_endpoint_mock():
    fake_image = b"fake image bytes"

    response = client.post(
        "/inspection/analyze-image",
        files={"file": ("ppe_violation_01.jpg", fake_image, "image/jpeg")}
    )

    assert response.status_code == 200

    data = response.json()

    assert "analysis" in data
    assert data["analysis"]["risk_level_guess"] in [
        "Low",
        "Medium",
        "High",
        "Review Needed"
    ]


def test_analyze_with_rules_endpoint_mock():
    fake_image = b"fake image bytes"

    response = client.post(
        "/inspection/analyze-with-rules",
        files={"file": ("ppe_violation_01.jpg", fake_image, "image/jpeg")},
        params={"top_k": 3}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "result" in data

    result = data["result"]

    assert "vlm_analysis" in result
    assert "rag_query" in result
    assert "retrieved_rules" in result

    assert len(result["retrieved_rules"]) > 0
    assert "rule_id" in result["retrieved_rules"][0]
    assert "score" in result["retrieved_rules"][0]


def test_generate_report_endpoint_mock():
    fake_image = b"fake image bytes"

    response = client.post(
        "/inspection/generate-report",
        files={"file": ("ppe_violation_01.jpg", fake_image, "image/jpeg")},
        params={"top_k": 3}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert "result" in data

    result = data["result"]

    assert "vlm_analysis" in result
    assert "retrieved_rules" in result
    assert "inspection_report" in result
    assert "latency_ms" in result
    assert "mlflow_run_id" in result

    report = result["inspection_report"]

    assert "inspection_id" in report
    assert "issue_detected" in report
    assert "issue_type" in report
    assert "severity" in report
    assert "recommended_action" in report

    assert report["severity"] in [
        "Low",
        "Medium",
        "High",
        "Review Needed"
    ]