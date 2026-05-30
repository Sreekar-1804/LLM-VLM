import base64
from fileinput import filename
import json
from tracemalloc import start
from urllib import response
from prompt_toolkit import prompt
import requests
from pathlib import Path
from typing import Dict


from app.backend.core.config import settings
from app.backend.schemas.inspection_schema import VLMAnalysis


class VLMService:
    def __init__(self):
        self.provider = settings.VLM_PROVIDER.lower()

    def analyze_image(self, image_bytes: bytes, filename: str = "uploaded_image.jpg") -> VLMAnalysis:
        if self.provider == "mock":
            return self._analyze_with_mock(filename)

        if self.provider == "openai":
            return self._analyze_with_openai(image_bytes, filename)

        if self.provider == "ollama":
            return self._analyze_with_ollama(image_bytes, filename)

        if self.provider == "gemini":
            return self._analyze_with_gemini(image_bytes, filename)

        raise ValueError(f"Unsupported VLM provider: {self.provider}")

    def _analyze_with_mock(self, filename: str) -> VLMAnalysis:
        """
        Mock response for local testing without external API calls.
        """

        filename_lower = filename.lower()

        if "helmet" in filename_lower or "ppe" in filename_lower:
            return VLMAnalysis(
                scene_description="A worker appears to be near industrial machinery without a clearly visible safety helmet.",
                visible_objects=["worker", "industrial machine", "production floor"],
                possible_issues=["missing helmet", "unsafe proximity to machinery"],
                risk_level_guess="High",
                uncertainty="Medium",
                raw_model_output="Mock VLM output based on filename."
            )

        if "crack" in filename_lower or "defect" in filename_lower:
            return VLMAnalysis(
                scene_description="A manufactured component appears to show visible surface damage or a possible crack.",
                visible_objects=["manufactured component", "surface defect", "inspection area"],
                possible_issues=["surface crack", "structural damage"],
                risk_level_guess="High",
                uncertainty="Medium",
                raw_model_output="Mock VLM output based on filename."
            )

        if "blocked" in filename_lower or "exit" in filename_lower:
            return VLMAnalysis(
                scene_description="An industrial walkway or emergency access area appears to be blocked by objects.",
                visible_objects=["walkway", "objects", "industrial area"],
                possible_issues=["blocked emergency exit", "unsafe access path"],
                risk_level_guess="High",
                uncertainty="Medium",
                raw_model_output="Mock VLM output based on filename."
            )

        return VLMAnalysis(
            scene_description="The image appears to show an industrial inspection scene, but no specific issue can be confirmed.",
            visible_objects=["industrial area"],
            possible_issues=["unclear visual evidence"],
            risk_level_guess="Review Needed",
            uncertainty="High",
            raw_model_output="Mock VLM output based on filename."
        )

    def _analyze_with_openai(self, image_bytes: bytes, filename: str) -> VLMAnalysis:
        """
        OpenAI vision analysis.

        Requires:
        OPENAI_API_KEY in .env
        VLM_PROVIDER=openai
        """

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is missing. Add it to .env or use VLM_PROVIDER=mock.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("OpenAI package not installed. Run: pip install openai") from exc

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        filename_lower = filename.lower()

        if filename_lower.endswith(".png"):
            mime_type = "image/png"
        elif filename_lower.endswith(".webp"):
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"

        prompt = """
            You are an industrial safety and quality inspection assistant.

            Analyze the uploaded inspection image and return ONLY valid JSON with this exact structure:

            {
            "scene_description": "short factual description of the visible scene",
            "visible_objects": ["object1", "object2"],
            "possible_issues": ["issue1", "issue2"],
            "risk_level_guess": "Low | Medium | High | Review Needed",
            "uncertainty": "Low | Medium | High"
            }

            Focus only on visible evidence.

            Inspection focus:
            - missing PPE such as helmet, vest, gloves, goggles, safety shoes
            - unsafe worker proximity to machines
            - exposed cables or electrical panels
            - blocked exits or blocked walkways
            - surface cracks or damaged parts
            - oil leakage, contamination, or unsafe floor conditions
            - missing labels or unreadable markings
            - blurry, dark, cropped, or unclear images

            Rules:
            - Do not invent details that are not visible.
            - If the image is unclear, set risk_level_guess to "Review Needed".
            - If evidence is uncertain, set uncertainty to "High".
            - Keep the output concise.
            """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        }
                    ],
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=500,
        )

        raw_output = response.choices[0].message.content

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise ValueError(f"OpenAI returned invalid JSON: {raw_output}") from exc

        return VLMAnalysis(
        scene_description=parsed.get("scene_description", ""),
        visible_objects=parsed.get("visible_objects", []),
        possible_issues=parsed.get("possible_issues", []),
        risk_level_guess=parsed.get("risk_level_guess", "Review Needed"),
        uncertainty=parsed.get("uncertainty", "High"),
        raw_model_output=raw_output
    )

    def _analyze_with_gemini(self, image_bytes: bytes, filename: str) -> VLMAnalysis:
        """
        Placeholder Gemini integration.

        We keep this placeholder so the architecture supports multiple providers.
        We will implement Gemini later only if needed.
        """

        raise NotImplementedError(
            "Gemini VLM provider is not implemented yet. Use VLM_PROVIDER=mock or VLM_PROVIDER=openai."
        )

    def _analyze_with_ollama(self, image_bytes: bytes, filename: str) -> VLMAnalysis:
        """
        Local Ollama vision analysis.

    Requires:
    - Ollama running locally
    - Vision model pulled, for example: ollama pull llava:7b
        """

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
You are an industrial safety and quality inspection assistant.

Analyze the uploaded inspection image and return ONLY valid JSON with this exact structure:

{
  "scene_description": "short factual description of the visible scene",
  "visible_objects": ["object1", "object2"],
  "possible_issues": ["issue1", "issue2"],
  "risk_level_guess": "Low | Medium | High | Review Needed",
  "uncertainty": "Low | Medium | High"
}

Focus only on visible evidence.

Inspection focus:
- missing PPE such as helmet, vest, gloves, goggles, safety shoes
- unsafe worker proximity to machines
- exposed cables or electrical panels
- blocked exits or blocked walkways
- surface cracks or damaged parts
- oil leakage, contamination, or unsafe floor conditions
- missing labels or unreadable markings
- blurry, dark, cropped, or unclear images

Rules:
- Do not invent details that are not visible.
- If the image is unclear, set risk_level_guess to "Review Needed".
- If no issue is visible, use possible_issues as an empty list and risk_level_guess as "Low".
- Return JSON only. No markdown. No explanation.
    """

        payload = {
            "model": settings.OLLAMA_VLM_MODEL,
            "prompt": prompt,
            "images": [image_base64],
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

        parsed = self._safe_parse_json(raw_output)

        return VLMAnalysis(
            scene_description=parsed.get("scene_description", ""),
            visible_objects=parsed.get("visible_objects", []),
            possible_issues=parsed.get("possible_issues", []),
            risk_level_guess=parsed.get("risk_level_guess", "Review Needed"),
            uncertainty=parsed.get("uncertainty", "High"),
            raw_model_output=raw_output
        )

    def _safe_parse_json(self, raw_output: str) -> Dict:
        """
    Tries to parse JSON even if the local model adds extra text.
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

        return {
            "scene_description": raw_output[:500],
            "visible_objects": [],
            "possible_issues": ["unclear visual evidence"],
            "risk_level_guess": "Review Needed",
            "uncertainty": "High"
    }

if __name__ == "__main__":
    service = VLMService()

    sample_image_path = Path("data/sample_images/sample_test.jpg")

    if sample_image_path.exists():
        image_bytes = sample_image_path.read_bytes()
        result = service.analyze_image(image_bytes, filename=sample_image_path.name)
    else:
        result = service.analyze_image(b"fake-image-bytes", filename="ppe_violation_helmet.jpg")

    print(result.model_dump_json(indent=4))