from app.backend.services.vlm_service import VLMService


def test_vlm_mock_ppe_output():
    service = VLMService()

    result = service.analyze_image(
        image_bytes=b"fake-image-bytes",
        filename="ppe_violation_01.jpg"
    )

    assert result.scene_description
    assert isinstance(result.visible_objects, list)
    assert isinstance(result.possible_issues, list)
    assert result.risk_level_guess in ["Low", "Medium", "High", "Review Needed"]
    assert result.uncertainty in ["Low", "Medium", "High"]


def test_vlm_mock_defect_output():
    service = VLMService()

    result = service.analyze_image(
        image_bytes=b"fake-image-bytes",
        filename="surface_crack_defect.jpg"
    )

    assert "crack" in " ".join(result.possible_issues).lower()
    assert result.risk_level_guess == "High"


def test_vlm_mock_unclear_output():
    service = VLMService()

    result = service.analyze_image(
        image_bytes=b"fake-image-bytes",
        filename="unknown_scene.jpg"
    )

    assert result.risk_level_guess == "Review Needed"
    assert result.uncertainty == "High"