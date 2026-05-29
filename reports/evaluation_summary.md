# VisionGuard AI Evaluation Summary

## Metrics

- total_cases: 8
- issue_keyword_accuracy: 1.0000
- severity_accuracy: 0.7500
- rule_retrieval_accuracy: 0.5000
- matched_rule_accuracy: 0.5000
- report_validity_rate: 1.0000
- human_review_rate: 1.0000
- average_latency_ms: 24.1537

## Notes

- Evaluation was performed in mock VLM/LLM mode.
- Mock mode is used to validate the pipeline structure before real API-based VLM evaluation.
- Rule retrieval accuracy may vary because FAISS performs semantic similarity search.
- Human review is intentionally triggered for high-severity and uncertain cases.