import json
from tracemalloc import start
from tracemalloc import start
from urllib import response
import uuid
from click import prompt
import requests
from typing import Dict, List

from app.backend.core.config import settings
from app.backend.schemas.inspection_schema import VLMAnalysis, InspectionReport


class LLMService:
    """
    LLM service for generating structured inspection reports.

    Supported providers:
    - mock: local deterministic report generation
    - openai: external LLM report generation
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

    def generate_inspection_report(
        self,
        vlm_analysis: VLMAnalysis,
        retrieved_rules: List[Dict]
    ) -> InspectionReport:
        if self.provider == "mock":
            return self._generate_with_mock(vlm_analysis, retrieved_rules)

        if self.provider == "openai":
            return self._generate_with_openai(vlm_analysis, retrieved_rules)
        
        if self.provider == "ollama":
            return self._generate_with_ollama(vlm_analysis, retrieved_rules)

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _generate_with_mock(
        self,
        vlm_analysis: VLMAnalysis,
        retrieved_rules: List[Dict]
    ) -> InspectionReport:
        """
        Deterministic local report generator.

        This is not a real LLM, but it allows the full pipeline to work
        without API keys.
        """

        inspection_id = f"VG-{uuid.uuid4().hex[:8].upper()}"

        primary_rule = retrieved_rules[0] if retrieved_rules else {}

        matched_rule_id = primary_rule.get("rule_id", "NO-RULE")
        matched_rule_text = primary_rule.get("text", "No matching rule found.")
        matched_rule_summary = self._summarize_rule_text(matched_rule_text)

        possible_issues = vlm_analysis.possible_issues

        if possible_issues:
            issue_type = possible_issues[0].title()
            issue_detected = issue_type.lower() != "unclear visual evidence"
        else:
            issue_type = "Unclear Visual Evidence"
            issue_detected = False

        severity = self._finalize_severity(
            vlm_severity=vlm_analysis.risk_level_guess,
            retrieved_rules=retrieved_rules
        )

        human_review_required = self._decide_human_review(
            severity=severity,
            uncertainty=vlm_analysis.uncertainty,
            retrieved_rules=retrieved_rules
        )

        recommended_action = self._extract_action_from_rule(matched_rule_text)

        if not recommended_action:
            recommended_action = "Send the case for human review before taking further action."

        confidence_note = self._build_confidence_note(vlm_analysis)

        return InspectionReport(
            inspection_id=inspection_id,
            issue_detected=issue_detected,
            issue_type=issue_type,
            severity=severity,
            visual_evidence=vlm_analysis.scene_description,
            matched_rule_id=matched_rule_id,
            matched_rule_summary=matched_rule_summary,
            recommended_action=recommended_action,
            human_review_required=human_review_required,
            confidence_note=confidence_note
        )

    def _generate_with_openai(
        self,
        vlm_analysis: VLMAnalysis,
        retrieved_rules: List[Dict]
    ) -> InspectionReport:
        """
        OpenAI report generation.

        Requires:
        OPENAI_API_KEY in .env
        LLM_PROVIDER=openai
        """

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is missing. Add it to .env or use LLM_PROVIDER=mock.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("OpenAI package not installed. Run: pip install openai") from exc

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        inspection_id = f"VG-{uuid.uuid4().hex[:8].upper()}"

        prompt = f"""
You are an industrial safety and quality inspection assistant.

Generate ONLY valid JSON matching this schema:

{{
  "inspection_id": "{inspection_id}",
  "issue_detected": true,
  "issue_type": "short issue category",
  "severity": "Low | Medium | High | Review Needed",
  "visual_evidence": "evidence from image analysis",
  "matched_rule_id": "most relevant rule id",
  "matched_rule_summary": "short rule summary",
  "recommended_action": "clear action based on the retrieved rule",
  "human_review_required": true,
  "confidence_note": "short note explaining confidence, uncertainty, or review need"
}}

Inputs:

VLM Analysis:
{vlm_analysis.model_dump_json(indent=2)}

Retrieved Rules:
{json.dumps(retrieved_rules, indent=2)}

Decision rules:
- Use only the retrieved rules.
- Do not invent rule IDs.
- Pick the most relevant retrieved rule as matched_rule_id.
- If visual evidence is unclear, set severity to "Review Needed".
- If severity is High or Review Needed, human_review_required must be true.
- If VLM uncertainty is Medium or High, human_review_required should be true.
- Keep the report concise and professional.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        raw_output = response.choices[0].message.content

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise ValueError(f"OpenAI returned invalid JSON: {raw_output}") from exc

        return InspectionReport(**parsed)

    def _summarize_rule_text(self, rule_text: str) -> str:
        for line in rule_text.splitlines():
            if line.startswith("Requirement:"):
                return line.replace("Requirement:", "").strip()

        return rule_text[:200].strip()

    def _extract_action_from_rule(self, rule_text: str) -> str:
        for line in rule_text.splitlines():
            if line.startswith("Recommended Action:"):
                return line.replace("Recommended Action:", "").strip()

            if line.startswith("Required Action:"):
                return line.replace("Required Action:", "").strip()

        return ""

    def _finalize_severity(
        self,
        vlm_severity: str,
        retrieved_rules: List[Dict]
    ) -> str:
        allowed = {"Low", "Medium", "High", "Review Needed"}

        rule_severities = [
            rule.get("severity", "")
            for rule in retrieved_rules
            if rule.get("severity", "") in allowed
        ]

        if "High" in rule_severities:
            return "High"

        if "Medium" in rule_severities:
            return "Medium"

        if vlm_severity in allowed:
            return vlm_severity

        return "Review Needed"

    def _decide_human_review(
        self,
        severity: str,
        uncertainty: str,
        retrieved_rules: List[Dict]
    ) -> bool:
        if severity in ["High", "Review Needed"]:
            return True

        if uncertainty in ["Medium", "High"]:
            return True

        for rule in retrieved_rules:
            text = rule.get("text", "")
            if "Human Review Required: Yes" in text:
                return True

        return False

    def _build_confidence_note(self, vlm_analysis: VLMAnalysis) -> str:
        if vlm_analysis.uncertainty == "High":
            return "The visual evidence is uncertain. Human review is required before making a final decision."

        if vlm_analysis.uncertainty == "Medium":
            return "The system detected a likely issue, but human review is recommended due to medium uncertainty."

        return "The system found clear visual evidence, but final operational decisions should still follow site review procedures."


    def _generate_with_ollama(
        self,
        vlm_analysis: VLMAnalysis,
        retrieved_rules: List[Dict]
    ) -> InspectionReport:
        """
        Local Ollama report generation.
        """

        inspection_id = f"VG-{uuid.uuid4().hex[:8].upper()}"

        prompt = f"""
    You are an industrial safety and quality inspection assistant.

    Generate ONLY valid JSON matching this schema:

    {{
    "inspection_id": "{inspection_id}",
    "issue_detected": true,
    "issue_type": "short issue category",
    "severity": "Low | Medium | High | Review Needed",
    "visual_evidence": "evidence from image analysis",
    "matched_rule_id": "most relevant rule id",
    "matched_rule_summary": "short rule summary",
    "recommended_action": "clear action based on the retrieved rule",
    "human_review_required": true,
    "confidence_note": "short note explaining confidence, uncertainty, or review need"
    }}

    Inputs:

    VLM Analysis:
    {vlm_analysis.model_dump_json(indent=2)}

    Retrieved Rules:
    {json.dumps(retrieved_rules, indent=2)}

    Decision rules:
    - Use only the retrieved rules.
    - Do not invent rule IDs.
    - Pick the most relevant retrieved rule as matched_rule_id.
    - If no issue is visible, set issue_detected to false and severity to "Low".
    - If visual evidence is unclear, set severity to "Review Needed".
    - If severity is High or Review Needed, human_review_required must be true.
    - If VLM uncertainty is Medium or High, human_review_required should be true.
    - Return JSON only. No markdown. No explanation.
    """

        payload = {
            "model": settings.OLLAMA_LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }

        response = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=180
    )

        response.raise_for_status()

        raw_output = response.json().get("response", "")

        parsed = self._safe_parse_json(raw_output, retrieved_rules)

        parsed["inspection_id"] = parsed.get("inspection_id", inspection_id)

        return InspectionReport(**parsed)


    def _safe_parse_json(
    self,
    raw_output: str,
    retrieved_rules: List[Dict] | None = None
    ) -> Dict:
        """
    Parses JSON from local LLM output.
    Local models sometimes add text before or after JSON.
        """

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        start = raw_output.find("{")
        end = raw_output.rfind("}")

        if start != -1 and end != -1 and end > start:
            json_text = raw_output[start:end + 1]
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                pass

        retrieved_rules = retrieved_rules or []
        primary_rule = retrieved_rules[0] if retrieved_rules else {}

        return {
            "inspection_id": f"VG-{uuid.uuid4().hex[:8].upper()}",
            "issue_detected": False,
            "issue_type": "Unclear Visual Evidence",
            "severity": "Review Needed",
            "visual_evidence": raw_output[:500],
            "matched_rule_id": primary_rule.get("rule_id", "NO-RULE"),
            "matched_rule_summary": primary_rule.get("text", "No matching rule found.")[:200],
            "recommended_action": "Send the case for human review before taking further action.",
            "human_review_required": True,
            "confidence_note": "The local model did not return valid structured JSON, so human review is required."
        }

if __name__ == "__main__":
    sample_vlm = VLMAnalysis(
        scene_description="A worker appears to be near industrial machinery without a clearly visible safety helmet.",
        visible_objects=["worker", "industrial machine", "production floor"],
        possible_issues=["missing helmet", "unsafe proximity to machinery"],
        risk_level_guess="High",
        uncertainty="Medium",
        raw_model_output="mock"
    )

    sample_rules = [
        {
            "rule_id": "PPE-001",
            "category": "Head Protection",
            "severity": "High",
            "source_file": "ppe_rules.md",
            "text": """## Rule ID: PPE-001
Category: Head Protection
Inspection Area: Active Machine Zone
Requirement: Workers must wear safety helmets when working near operating machinery, moving equipment, or overhead hazard areas.
Severity: High
Recommended Action: Stop work temporarily and ensure the worker wears an approved safety helmet before resuming operations.
Human Review Required: Yes""",
            "score": 0.72
        }
    ]

    service = LLMService()
    report = service.generate_inspection_report(sample_vlm, sample_rules)

    print(report.model_dump_json(indent=4))