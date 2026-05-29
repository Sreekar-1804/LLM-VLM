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
