import time
from typing import Dict

from app.backend.schemas.inspection_schema import VLMAnalysis
from app.backend.services.rag_service import RAGService
from app.backend.services.vlm_service import VLMService
from app.backend.services.llm_service import LLMService
from app.backend.services.logging_service import MLflowLoggingService


class InspectionPipelineService:
    """
    End-to-end inspection pipeline.

    Current full pipeline:
    Image -> VLM analysis -> RAG query -> relevant rules -> structured inspection report -> MLflow tracking
    """

    def __init__(self):
        self.vlm_service = VLMService()
        self.rag_service = RAGService()
        self.llm_service = LLMService()
        self.logging_service = MLflowLoggingService()

    def build_rag_query(self, vlm_analysis: VLMAnalysis) -> str:
        query_parts = []

        if vlm_analysis.scene_description:
            query_parts.append(vlm_analysis.scene_description)

        if vlm_analysis.visible_objects:
            query_parts.append("Visible objects: " + ", ".join(vlm_analysis.visible_objects))

        if vlm_analysis.possible_issues:
            query_parts.append("Possible issues: " + ", ".join(vlm_analysis.possible_issues))

        if vlm_analysis.risk_level_guess:
            query_parts.append("Risk level: " + vlm_analysis.risk_level_guess)

        if vlm_analysis.uncertainty:
            query_parts.append("Uncertainty: " + vlm_analysis.uncertainty)

        return " | ".join(query_parts).strip()

    def analyze_image_with_rules(
        self,
        image_bytes: bytes,
        filename: str,
        top_k: int = 3
    ) -> Dict:
        vlm_analysis = self.vlm_service.analyze_image(
            image_bytes=image_bytes,
            filename=filename
        )

        rag_query = self.build_rag_query(vlm_analysis)

        retrieved_rules = self.rag_service.retrieve_rules(
            query=rag_query,
            top_k=top_k
        )

        return {
            "filename": filename,
            "vlm_analysis": vlm_analysis.model_dump(),
            "rag_query": rag_query,
            "retrieved_rules": retrieved_rules
        }

    def generate_full_inspection_report(
        self,
        image_bytes: bytes,
        filename: str,
        top_k: int = 3,
        enable_tracking: bool = True
    ) -> Dict:
        start_time = time.perf_counter()

        vlm_analysis = self.vlm_service.analyze_image(
            image_bytes=image_bytes,
            filename=filename
        )

        rag_query = self.build_rag_query(vlm_analysis)

        retrieved_rules = self.rag_service.retrieve_rules(
            query=rag_query,
            top_k=top_k
        )

        inspection_report = self.llm_service.generate_inspection_report(
            vlm_analysis=vlm_analysis,
            retrieved_rules=retrieved_rules
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        result = {
            "filename": filename,
            "vlm_analysis": vlm_analysis.model_dump(),
            "rag_query": rag_query,
            "retrieved_rules": retrieved_rules,
            "inspection_report": inspection_report.model_dump(),
            "latency_ms": latency_ms,
            "mlflow_run_id": None
        }

        if enable_tracking:
            run_id = self.logging_service.log_inspection_run(
                filename=filename,
                vlm_analysis=result["vlm_analysis"],
                rag_query=rag_query,
                retrieved_rules=retrieved_rules,
                inspection_report=result["inspection_report"],
                top_k=top_k,
                latency_ms=latency_ms
            )

            result["mlflow_run_id"] = run_id

        return result


if __name__ == "__main__":
    from pathlib import Path

    service = InspectionPipelineService()

    sample_image_path = Path("data/sample_images/sample_test.jpg")

    if not sample_image_path.exists():
        raise FileNotFoundError(
            "Add a real test image at data/sample_images/sample_test.jpg before running real API mode."
        )

    result = service.generate_full_inspection_report(
        image_bytes=sample_image_path.read_bytes(),
        filename=sample_image_path.name,
        top_k=3,
        enable_tracking=True
    )

    print("Filename:", result["filename"])
    print("Latency:", result["latency_ms"], "ms")
    print("MLflow Run ID:", result["mlflow_run_id"])

    print("\nVLM Analysis:")
    print(result["vlm_analysis"])

    print("\nRetrieved Rules:")
    for rule in result["retrieved_rules"]:
        print(rule["rule_id"], "-", rule["category"], "-", rule["severity"])

    print("\nFinal Inspection Report:")
    print(result["inspection_report"])