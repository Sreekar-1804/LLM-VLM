from app.backend.services.report_service import InspectionPipelineService


def test_pipeline_analyze_image_with_rules():
    service = InspectionPipelineService()

    result = service.analyze_image_with_rules(
        image_bytes=b"fake-image-bytes",
        filename="ppe_violation_01.jpg",
        top_k=3
    )

    assert "filename" in result
    assert "vlm_analysis" in result
    assert "rag_query" in result
    assert "retrieved_rules" in result

    assert result["filename"] == "ppe_violation_01.jpg"
    assert len(result["retrieved_rules"]) > 0


def test_pipeline_generate_full_report_without_tracking():
    service = InspectionPipelineService()

    result = service.generate_full_inspection_report(
        image_bytes=b"fake-image-bytes",
        filename="ppe_violation_01.jpg",
        top_k=3,
        enable_tracking=False
    )

    assert "inspection_report" in result
    assert "latency_ms" in result
    assert result["mlflow_run_id"] is None

    report = result["inspection_report"]

    assert "inspection_id" in report
    assert "severity" in report
    assert "recommended_action" in report