from pydantic import BaseModel, Field
from typing import List, Optional


class VLMAnalysis(BaseModel):
    scene_description: str = Field(
        ...,
        description="Short description of what is visible in the inspection image."
    )
    visible_objects: List[str] = Field(
        default_factory=list,
        description="Objects or entities visible in the image."
    )
    possible_issues: List[str] = Field(
        default_factory=list,
        description="Potential safety or quality issues visible in the image."
    )
    risk_level_guess: str = Field(
        ...,
        description="Initial risk guess: Low, Medium, High, or Review Needed."
    )
    uncertainty: str = Field(
        ...,
        description="Uncertainty level: Low, Medium, or High."
    )
    raw_model_output: Optional[str] = Field(
        default=None,
        description="Raw model output for debugging or audit purposes."
    )


class InspectionReport(BaseModel):
    inspection_id: str = Field(
        ...,
        description="Unique inspection identifier."
    )
    issue_detected: bool = Field(
        ...,
        description="Whether an issue was detected."
    )
    issue_type: str = Field(
        ...,
        description="Main issue category detected."
    )
    severity: str = Field(
        ...,
        description="Final severity: Low, Medium, High, or Review Needed."
    )
    visual_evidence: str = Field(
        ...,
        description="Evidence observed from the image analysis."
    )
    matched_rule_id: str = Field(
        ...,
        description="Most relevant retrieved rule ID."
    )
    matched_rule_summary: str = Field(
        ...,
        description="Short summary of the matched inspection rule."
    )
    recommended_action: str = Field(
        ...,
        description="Recommended action based on the issue and rule."
    )
    human_review_required: bool = Field(
        ...,
        description="Whether a human reviewer must verify the case."
    )
    confidence_note: str = Field(
        ...,
        description="Short note about confidence, uncertainty, or review need."
    )