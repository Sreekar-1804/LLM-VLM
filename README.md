Below is a polished **final README** for your GitHub repo. Replace your current `README.md` with this.

````markdown
# VisionGuard AI  
## Multimodal Industrial Inspection Assistant using LLM, VLM, RAG and MLOps

VisionGuard AI is an industry-focused multimodal AI system for industrial safety and quality inspection. The system analyzes inspection images, retrieves relevant safety or quality rules, and generates structured inspection reports using a Vision-Language Model, Retrieval-Augmented Generation, and LLM-based report generation.

The project is designed as an AI Engineering and MLOps portfolio project, not just a simple chatbot or notebook demo.

---

## Project Overview

Industrial inspection workflows often require human reviewers to check images for safety risks, PPE violations, machine hazards, blocked access paths, damaged components, or quality defects.

VisionGuard AI supports this workflow by providing an AI-assisted inspection pipeline:

```text
Image Upload
   ↓
VLM Image Understanding
   ↓
RAG-Based Rule Retrieval
   ↓
LLM Structured Report Generation
   ↓
MLflow Tracking
   ↓
Streamlit Dashboard
````

The system is designed for human-in-the-loop inspection, meaning it does not make final operational decisions automatically. High-risk or uncertain cases are marked for human review.

---

## Industry Use Case

This project focuses on industrial safety and quality inspection scenarios such as:

* Missing helmet or PPE violation
* Unsafe worker proximity to machinery
* Blocked emergency exits
* Exposed cables or unsafe machine areas
* Surface cracks or damaged components
* Missing labels or barcode issues
* Oil leakage or contamination
* Unclear or blurry inspection evidence

The use case is relevant to:

* Manufacturing
* Automotive production
* Industrial safety
* Quality control
* Industry 4.0
* AI-assisted inspection systems

---

## Key Features

* Vision-Language Model service for image understanding
* Mock VLM mode for local testing without API keys
* Optional OpenAI-based VLM/LLM integration
* Custom industrial inspection rule knowledge base
* FAISS-based semantic retrieval pipeline
* Sentence Transformer embeddings
* LLM-based structured inspection report generation
* FastAPI backend for model serving
* Streamlit frontend for interactive demo
* MLflow tracking for inspection auditability
* Evaluation workflow with labeled test cases
* Pytest-based test suite
* Docker Compose deployment
* GitHub Actions CI pipeline

---

## Architecture

```text
                        ┌────────────────────┐
                        │  Streamlit Frontend │
                        │  Image Upload UI    │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │   FastAPI Backend   │
                        │   REST Endpoints    │
                        └─────────┬──────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
     │  VLM Service   │   │  RAG Service   │   │  LLM Service   │
     │ Image Analysis │   │ Rule Retrieval │   │ Report Output  │
     └───────┬────────┘   └───────┬────────┘   └───────┬────────┘
             │                    │                    │
             ▼                    ▼                    ▼
     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
     │ Scene Summary  │   │ FAISS Vector DB│   │ JSON Report    │
     │ Possible Issues│   │ Rule Chunks    │   │ Severity/Action│
     └────────────────┘   └────────────────┘   └────────────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │      MLflow        │
                        │ Tracking + Logs    │
                        └────────────────────┘
```

---

## System Workflow

### 1. Image Analysis

The uploaded image is analyzed by the VLM service.

Example output:

```json
{
  "scene_description": "A worker appears to be near industrial machinery without a clearly visible safety helmet.",
  "visible_objects": ["worker", "industrial machine", "production floor"],
  "possible_issues": ["missing helmet", "unsafe proximity to machinery"],
  "risk_level_guess": "High",
  "uncertainty": "Medium"
}
```

### 2. Rule Retrieval

The VLM output is converted into a semantic query and passed to the RAG pipeline.

Example query:

```text
worker missing helmet near active machinery unsafe PPE violation
```

The FAISS retriever returns relevant inspection rules such as:

```text
PPE-001: Head Protection
MACH-005: Unsafe Worker Distance
ESC-003: High Severity Issue
```

### 3. Structured Report Generation

The LLM service generates a structured inspection report.

Example output:

```json
{
  "inspection_id": "VG-A1B2C3D4",
  "issue_detected": true,
  "issue_type": "Missing Helmet",
  "severity": "High",
  "visual_evidence": "A worker appears to be near industrial machinery without a clearly visible safety helmet.",
  "matched_rule_id": "PPE-001",
  "matched_rule_summary": "Workers must wear safety helmets when working near operating machinery.",
  "recommended_action": "Stop work temporarily and ensure the worker wears an approved safety helmet before resuming operations.",
  "human_review_required": true,
  "confidence_note": "The system detected a likely issue, but human review is recommended due to medium uncertainty."
}
```

---

## Tech Stack

### AI and ML

* Python
* Vision-Language Model service
* LLM-based report generation
* Sentence Transformers
* FAISS vector search
* Retrieval-Augmented Generation

### Backend

* FastAPI
* Pydantic
* Uvicorn
* REST API architecture

### Frontend

* Streamlit
* Requests

### MLOps and Engineering

* MLflow
* Docker
* Docker Compose
* Pytest
* GitHub Actions
* Git/GitHub

### Data and Evaluation

* Pandas
* Custom markdown rule knowledge base
* Evaluation CSV
* Structured report validation

---

## Project Structure

```text
visionguard-ai/
│
├── app/
│   ├── backend/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   └── inspection_routes.py
│   │   ├── services/
│   │   │   ├── rag_service.py
│   │   │   ├── vlm_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── report_service.py
│   │   │   ├── logging_service.py
│   │   │   └── rule_loader.py
│   │   ├── schemas/
│   │   │   └── inspection_schema.py
│   │   └── core/
│   │       ├── config.py
│   │       └── prompts.py
│   │
│   └── frontend/
│       └── streamlit_app.py
│
├── data/
│   ├── inspection_rules/
│   │   ├── ppe_rules.md
│   │   ├── machine_safety_rules.md
│   │   ├── defect_rules.md
│   │   └── escalation_policy.md
│   │
│   ├── sample_images/
│   └── eval/
│       └── evaluation_labels.csv
│
├── notebooks/
│   ├── 01_rag_pipeline.ipynb
│   ├── 02_vlm_testing.ipynb
│   ├── 03_end_to_end_pipeline.ipynb
│   └── 04_evaluation.ipynb
│
├── reports/
│   ├── evaluation_results.csv
│   └── evaluation_summary.md
│
├── tests/
│   ├── test_api.py
│   ├── test_schema.py
│   ├── test_rag.py
│   ├── test_vlm.py
│   ├── test_llm.py
│   ├── test_pipeline.py
│   └── test_evaluation_files.py
│
├── vector_store/
├── logs/
├── mlruns/
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sreekar-1804/LLM-VLM.git
cd LLM-VLM
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate on Windows:

```bash
venv\Scripts\activate
```

Activate on macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a `.env` file using `.env.example`.

For local mock mode:

```env
OPENAI_API_KEY=
GOOGLE_API_KEY=

VLM_PROVIDER=mock
LLM_PROVIDER=mock

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RETRIEVAL_TOP_K=3

MLFLOW_TRACKING_URI=mlruns
```

Mock mode allows the project to run without external API keys.

---

## Build FAISS Vector Store

Before running the backend, build the FAISS index:

```bash
python -m app.backend.services.rag_service
```

This creates:

```text
vector_store/faiss_index.bin
vector_store/rule_chunks.json
```

---

## Run Locally

### Terminal 1: Start FastAPI backend

```bash
uvicorn app.backend.main:app --reload
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

### Terminal 2: Start Streamlit frontend

```bash
streamlit run app/frontend/streamlit_app.py
```

Streamlit app:

```text
http://127.0.0.1:8501
```

### Terminal 3: Start MLflow UI

On Windows:

```bash
mlflow ui --backend-store-uri file:///D:/visionguard-ai/mlruns --port 5000
```

For generic local use:

```bash
mlflow ui --backend-store-uri mlruns --port 5000
```

MLflow UI:

```text
http://127.0.0.1:5000
```

---

## Run with Docker

The project includes Docker Compose setup for:

* FastAPI backend
* Streamlit frontend
* MLflow UI

### Build containers

```bash
docker compose build
```

### Run full stack

```bash
docker compose up
```

Open:

```text
FastAPI Docs: http://127.0.0.1:8000/docs
Streamlit App: http://127.0.0.1:8501
MLflow UI: http://127.0.0.1:5000
```

### Stop containers

```bash
docker compose down
```

---

## API Endpoints

### Health Check

```http
GET /health
```

### Search Rules

```http
POST /inspection/search-rules
```

Request:

```json
{
  "query": "worker missing helmet near operating machinery",
  "top_k": 3
}
```

### Analyze Image

```http
POST /inspection/analyze-image
```

Returns VLM-based image analysis.

### Analyze Image with Rules

```http
POST /inspection/analyze-with-rules
```

Returns:

* VLM analysis
* generated RAG query
* retrieved inspection rules

### Generate Full Inspection Report

```http
POST /inspection/generate-report
```

Returns:

* VLM analysis
* RAG query
* retrieved rules
* final structured inspection report
* latency
* MLflow run ID

---

## MLflow Tracking

VisionGuard AI logs inspection runs using MLflow.

Tracked information includes:

* filename
* VLM provider
* LLM provider
* embedding model
* retrieval top-k
* retrieved rule IDs
* matched rule ID
* severity
* issue type
* latency
* human review requirement
* final inspection report JSON

MLflow provides auditability and reproducibility for inspection runs.

---

## Evaluation

The project includes an evaluation workflow for measuring pipeline reliability.

Evaluation metrics include:

* issue keyword accuracy
* severity classification accuracy
* rule retrieval accuracy
* matched rule accuracy
* structured report validity
* average latency
* human review rate

Evaluation files:

```text
data/eval/evaluation_labels.csv
reports/evaluation_results.csv
reports/evaluation_summary.md
```

Current evaluation uses mock VLM/LLM mode to validate pipeline structure before real VLM API-based testing.

---

## Testing

The project includes a Pytest-based test suite covering:

* FastAPI health and inspection endpoints
* Pydantic schema validation
* VLM mock image analysis
* LLM structured report generation
* FAISS-based RAG retrieval
* End-to-end inspection pipeline
* Evaluation file validation

Run tests:

```bash
python -m pytest
```

---

## Continuous Integration

The project includes a GitHub Actions workflow that runs automated tests on every push and pull request.

The CI pipeline:

* sets up Python 3.11
* installs project dependencies
* builds the FAISS vector store
* runs the Pytest suite

Workflow file:

```text
.github/workflows/test.yml
```

---

## Current Project Status

* Phase 0: Project setup completed
* Phase 1: Inspection rule knowledge base completed
* Phase 2: RAG pipeline with FAISS and Sentence Transformers completed
* Phase 3: VLM image understanding service completed
* Phase 4: Multimodal VLM-to-RAG pipeline completed
* Phase 5: LLM-based structured inspection report generation completed
* Phase 6: Streamlit frontend integration completed
* Phase 7: MLflow tracking completed
* Phase 8: Evaluation system completed
* Phase 9: Testing hardening completed
* Phase 10: Dockerized deployment completed
* Phase 11: GitHub Actions CI completed

---

## Limitations

This project is designed as an AI engineering portfolio system and not as a certified industrial safety tool.

Current limitations:

* Mock mode uses filenames to simulate VLM behavior
* Real VLM performance depends on selected API provider
* No real industrial dataset has been used yet
* Rule base is manually created and simplified
* No production database is connected
* No role-based user management
* No Kubernetes deployment
* Human review is still required for high-risk cases

---

## Future Improvements

Potential improvements include:

* Real VLM evaluation using actual industrial inspection images
* OpenAI or Gemini-based production VLM mode
* Local VLM support using LLaVA or Qwen-VL
* Hybrid retrieval using keyword search and vector search
* Reranking retrieved rules
* PostgreSQL database for inspection history
* Authentication and user roles
* PDF report generation
* Prometheus/Grafana monitoring
* Cloud deployment
* Kubernetes orchestration
* ONNX/TensorRT optimization for edge AI use cases

---

## Project Highlights

This project demonstrates practical skills in:

* LLM/VLM application development
* Multimodal AI pipeline design
* Retrieval-Augmented Generation
* Vector search using FAISS
* FastAPI backend development
* Streamlit frontend development
* MLOps with MLflow
* Dockerized deployment
* Automated testing with Pytest
* CI workflow using GitHub Actions
* Evaluation and failure analysis

---

## Interview Summary

VisionGuard AI is an end-to-end multimodal industrial inspection assistant. The system takes an inspection image, analyzes it using a VLM service, retrieves relevant safety or quality rules using a FAISS-based RAG pipeline, and generates a structured inspection report using an LLM service.

I designed the system with production-style components including FastAPI serving, Streamlit UI, MLflow tracking, Docker Compose deployment, Pytest validation, and GitHub Actions CI. The project focuses on industrial safety and quality inspection scenarios and follows a human-in-the-loop approach for high-risk or uncertain cases.

---

## Repository

GitHub:

```text
https://github.com/Sreekar-1804/LLM-VLM
```

````

After pasting, run:

```powershell
git add README.md
git commit -m "Add final professional README"
git push
````
