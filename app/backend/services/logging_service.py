import json
import time
from pathlib import Path
from typing import Dict, List, Any

import mlflow

from app.backend.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MLRUNS_DIR = PROJECT_ROOT / "mlruns"


class MLflowLoggingService:
    """
    MLflow logging service for inspection runs.

    Tracks:
    - model/provider settings
    - retrieval parameters
    - retrieved rule IDs
    - report outputs
    - latency
    - final severity and review decision
    """

    def __init__(self):
        tracking_uri = settings.MLFLOW_TRACKING_URI
        if tracking_uri == "mlruns":
            tracking_uri = MLRUNS_DIR.resolve().as_uri()

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("visionguard-inspection-runs")

    def log_inspection_run(
        self,
        filename: str,
        vlm_analysis: Dict[str, Any],
        rag_query: str,
        retrieved_rules: List[Dict[str, Any]],
        inspection_report: Dict[str, Any],
        top_k: int,
        latency_ms: float,
    ) -> str:
        """
        Logs a complete inspection run to MLflow.

        Returns:
            MLflow run ID
        """

        retrieved_rule_ids = [
            rule.get("rule_id", "UNKNOWN")
            for rule in retrieved_rules
        ]

        retrieved_rule_scores = [
            float(rule.get("score", 0.0))
            for rule in retrieved_rules
        ]

        with mlflow.start_run(run_name=inspection_report.get("inspection_id", "inspection-run")) as run:
            run_id = run.info.run_id

            # Parameters
            mlflow.log_param("filename", filename)
            mlflow.log_param("vlm_provider", settings.VLM_PROVIDER)
            mlflow.log_param("llm_provider", settings.LLM_PROVIDER)
            mlflow.log_param("embedding_model", settings.EMBEDDING_MODEL)
            mlflow.log_param("retrieval_top_k", top_k)
            mlflow.log_param("retrieved_rule_ids", ",".join(retrieved_rule_ids))
            mlflow.log_param("matched_rule_id", inspection_report.get("matched_rule_id", "UNKNOWN"))

            # Metrics
            mlflow.log_metric("latency_ms", latency_ms)
            mlflow.log_metric("retrieved_rule_count", len(retrieved_rules))
            mlflow.log_metric("human_review_required", int(bool(inspection_report.get("human_review_required", False))))
            mlflow.log_metric("issue_detected", int(bool(inspection_report.get("issue_detected", False))))

            if retrieved_rule_scores:
                mlflow.log_metric("top_rule_score", retrieved_rule_scores[0])
                mlflow.log_metric("avg_rule_score", sum(retrieved_rule_scores) / len(retrieved_rule_scores))

            # Tags
            mlflow.set_tag("severity", inspection_report.get("severity", "Unknown"))
            mlflow.set_tag("issue_type", inspection_report.get("issue_type", "Unknown"))
            mlflow.set_tag("project", "VisionGuard AI")
            mlflow.set_tag("pipeline", "VLM-RAG-LLM")

            # Artifacts
            artifact_payload = {
                "filename": filename,
                "vlm_analysis": vlm_analysis,
                "rag_query": rag_query,
                "retrieved_rules": retrieved_rules,
                "inspection_report": inspection_report,
                "latency_ms": latency_ms,
                "logged_at_unix": time.time(),
            }

            artifact_path = PROJECT_ROOT / "logs" / f"{inspection_report.get('inspection_id', run_id)}.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)

            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(artifact_payload, f, indent=4, ensure_ascii=False)

            mlflow.log_artifact(str(artifact_path), artifact_path="inspection_outputs")

            return run_id