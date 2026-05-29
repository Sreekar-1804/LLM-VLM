from pydantic import ValidationError
import pytest

from app.backend.schemas.inspection_schema import VLMAnalysis, InspectionReport


def test_vlm_analysis_schema():
    analysis = VLMAnalysis(
        scene_description="Worker near machine without helmet.",
        visible_objects=["worker", "machine"],
        possible_issues=["missing helmet"],
        risk_level_guess="High",
        uncertainty="Medium",
        raw_model_output="test"
    )

    assert analysis.scene_description
    assert "worker" in analysis.visible_objects
    assert analysis.risk_level_guess == "High"


def test_inspection_report_schema():
    report = InspectionReport(
        inspection_id="VG-TEST123",
        issue_detected=True,
        issue_type="Missing Helmet",
        severity="High",
        visual_evidence="Worker near machine without helmet.",
        matched_rule_id="PPE-001",
        matched_rule_summary="Helmet required in active machine zones.",
        recommended_action="Stop work and correct PPE violation.",
        human_review_required=True,
        confidence_note="Human review recommended."
    )

    assert report.issue_detected is True
    assert report.severity == "High"
    assert report.human_review_required is True


def test_vlm_schema_requires_scene_description():
    with pytest.raises(ValidationError):
        VLMAnalysis(
            visible_objects=["worker"],
            possible_issues=["missing helmet"],
            risk_level_guess="High",
            uncertainty="Medium"
        )


def test_report_schema_requires_inspection_id():
    with pytest.raises(ValidationError):
        InspectionReport(
            issue_detected=True,
            issue_type="Missing Helmet",
            severity="High",
            visual_evidence="Worker near machine without helmet.",
            matched_rule_id="PPE-001",
            matched_rule_summary="Helmet required.",
            recommended_action="Stop work.",
            human_review_required=True,
            confidence_note="Review required."
        )