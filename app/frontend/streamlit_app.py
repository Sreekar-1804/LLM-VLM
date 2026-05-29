import json
from datetime import datetime

import requests
import streamlit as st

import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="VisionGuard AI",
    page_icon="🛡️",
    layout="wide"
)


st.title("VisionGuard AI")
st.subheader("Multimodal Industrial Inspection Assistant")

st.write(
    """
    Upload an industrial inspection image to generate an AI-assisted safety or quality inspection report.
    
    Pipeline:
    Image → VLM Analysis → RAG Rule Retrieval → LLM Structured Report
    """
)


with st.sidebar:
    st.header("Settings")

    top_k = st.slider(
        "Number of rules to retrieve",
        min_value=1,
        max_value=5,
        value=3
    )

    st.markdown("---")

    st.write("Backend status:")

    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=5)

        if health_response.status_code == 200:
            st.success("Backend connected")
        else:
            st.error("Backend not healthy")
    except requests.exceptions.RequestException:
        st.error("Backend not running")

    st.markdown("---")

    st.caption(
        "Run backend with: uvicorn app.backend.main:app --reload"
    )


uploaded_file = st.file_uploader(
    "Upload inspection image",
    type=["jpg", "jpeg", "png"]
)


if uploaded_file is not None:
    st.markdown("## Uploaded Image")

    st.image(
        uploaded_file,
        caption=uploaded_file.name,
        use_container_width=True
    )

    if st.button("Run Inspection", type="primary"):
        with st.spinner("Running multimodal inspection pipeline..."):
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                params = {
                    "top_k": top_k
                }

                response = requests.post(
                    f"{BACKEND_URL}/inspection/generate-report",
                    files=files,
                    params=params,
                    timeout=120
                )

                if response.status_code != 200:
                    st.error("Backend returned an error.")
                    st.code(response.text)
                    st.stop()

                data = response.json()

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to backend. Start FastAPI first using: "
                    "uvicorn app.backend.main:app --reload"
                )
                st.stop()

            except requests.exceptions.Timeout:
                st.error("Request timed out. The backend took too long to respond.")
                st.stop()

            except Exception as error:
                st.error(f"Unexpected error: {error}")
                st.stop()

        result = data.get("result", {})

        vlm_analysis = result.get("vlm_analysis", {})
        rag_query = result.get("rag_query", "")
        retrieved_rules = result.get("retrieved_rules", [])
        inspection_report = result.get("inspection_report", {})
        latency_ms = result.get("latency_ms", None)
        mlflow_run_id = result.get("mlflow_run_id", None)

        st.success("Inspection completed")

        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Final Report",
                "VLM Analysis",
                "Retrieved Rules",
                "Raw JSON"
            ]
        )

        with tab1:
            st.markdown("## Final Inspection Report")
            if latency_ms is not None:
                st.caption(f"Pipeline latency: {latency_ms} ms")

            if mlflow_run_id:
                st.caption(f"MLflow Run ID: {mlflow_run_id}")

            severity = inspection_report.get("severity", "Unknown")

            if severity == "High":
                st.error(f"Severity: {severity}")
            elif severity == "Medium":
                st.warning(f"Severity: {severity}")
            elif severity == "Low":
                st.info(f"Severity: {severity}")
            else:
                st.warning(f"Severity: {severity}")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Issue Detected",
                    str(inspection_report.get("issue_detected", "Unknown"))
                )

                st.metric(
                    "Human Review Required",
                    str(inspection_report.get("human_review_required", "Unknown"))
                )

            with col2:
                st.metric(
                    "Issue Type",
                    inspection_report.get("issue_type", "Unknown")
                )

                st.metric(
                    "Matched Rule",
                    inspection_report.get("matched_rule_id", "Unknown")
                )

            st.markdown("### Visual Evidence")
            st.write(inspection_report.get("visual_evidence", "Not available"))

            st.markdown("### Matched Rule Summary")
            st.write(inspection_report.get("matched_rule_summary", "Not available"))

            st.markdown("### Recommended Action")
            st.write(inspection_report.get("recommended_action", "Not available"))

            st.markdown("### Confidence Note")
            st.write(inspection_report.get("confidence_note", "Not available"))

            report_download = {
                "generated_at": datetime.now().isoformat(),
                "filename": uploaded_file.name,
                "inspection_report": inspection_report,
                "vlm_analysis": vlm_analysis,
                "retrieved_rules": retrieved_rules,
                "rag_query": rag_query
            }

            st.download_button(
                label="Download Inspection Report JSON",
                data=json.dumps(report_download, indent=4),
                file_name=f"inspection_report_{uploaded_file.name}.json",
                mime="application/json"
            )

        with tab2:
            st.markdown("## VLM Image Analysis")

            st.markdown("### Scene Description")
            st.write(vlm_analysis.get("scene_description", "Not available"))

            st.markdown("### Visible Objects")
            visible_objects = vlm_analysis.get("visible_objects", [])

            if visible_objects:
                for obj in visible_objects:
                    st.write(f"- {obj}")
            else:
                st.write("No visible objects returned.")

            st.markdown("### Possible Issues")
            possible_issues = vlm_analysis.get("possible_issues", [])

            if possible_issues:
                for issue in possible_issues:
                    st.write(f"- {issue}")
            else:
                st.write("No possible issues returned.")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Risk Level Guess",
                    vlm_analysis.get("risk_level_guess", "Unknown")
                )

            with col2:
                st.metric(
                    "Uncertainty",
                    vlm_analysis.get("uncertainty", "Unknown")
                )

            with st.expander("Raw VLM Output"):
                st.write(vlm_analysis.get("raw_model_output", "Not available"))

        with tab3:
            st.markdown("## Retrieved Inspection Rules")

            st.markdown("### Generated RAG Query")
            st.code(rag_query)

            if retrieved_rules:
                for idx, rule in enumerate(retrieved_rules, start=1):
                    with st.expander(
                        f"{idx}. {rule.get('rule_id', 'Unknown')} - "
                        f"{rule.get('category', 'Unknown')} "
                        f"(Score: {round(rule.get('score', 0), 4)})"
                    ):
                        st.write("Severity:", rule.get("severity", "Unknown"))
                        st.write("Source file:", rule.get("source_file", "Unknown"))
                        st.markdown("Rule text:")
                        st.code(rule.get("text", "No rule text available"))
            else:
                st.warning("No rules retrieved.")

        with tab4:
            st.markdown("## Raw Pipeline Output")
            st.json(data)

else:
    st.info("Upload an inspection image to start.")