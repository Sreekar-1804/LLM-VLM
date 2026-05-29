from app.backend.schemas.inspection_schema import VLMAnalysis
from app.backend.services.llm_service import LLMService


def test_llm_mock_generates_report():
    service = LLMService()

    vlm_analysis = VLMAnalysis(
        scene_description="A worker appears to be near machinery without a helmet.",
        visible_objects=["worker", "machine"],
        possible_issues=["missing helmet"],
        risk_level_guess="High",
        uncertainty="Medium",
        raw_model_output="mock"
    )

    retrieved_rules = [
        {
            "rule_id": "PPE-001",
            "category": "Head Protection",
            "severity": "High",
            "source_file": "ppe_rules.md",
            "text": """## Rule ID: PPE-001
Category: Head Protection
Requirement: Workers must wear safety helmets near operating machinery.
Severity: High
Recommended Action: Stop work until helmet compliance is restored.
Human Review Required: Yes""",
            "score": 0.8
        }
    ]

    report = service.generate_inspection_report(
        vlm_analysis=vlm_analysis,
        retrieved_rules=retrieved_rules
    )

    assert report.inspection_id.startswith("VG-")
    assert report.issue_detected is True
    assert report.issue_type == "Missing Helmet"
    assert report.severity == "High"
    assert report.matched_rule_id == "PPE-001"
    assert report.human_review_required is True
    assert report.recommended_action


def test_llm_mock_handles_no_rules():
    service = LLMService()

    vlm_analysis = VLMAnalysis(
        scene_description="The image is unclear.",
        visible_objects=["industrial area"],
        possible_issues=["unclear visual evidence"],
        risk_level_guess="Review Needed",
        uncertainty="High",
        raw_model_output="mock"
    )

    report = service.generate_inspection_report(
        vlm_analysis=vlm_analysis,
        retrieved_rules=[]
    )

    assert report.issue_detected is False
    assert report.severity == "Review Needed"
    assert report.human_review_required is True
    assert report.matched_rule_id == "NO-RULE"