from fastapi import FastAPI

from app.backend.routes.inspection_routes import router as inspection_router


app = FastAPI(
    title="VisionGuard AI",
    description="Multimodal Industrial Inspection Assistant using LLM, VLM, RAG and MLOps",
    version="0.1.0"
)


app.include_router(inspection_router)


@app.get("/")
def root():
    return {
        "message": "VisionGuard AI backend is running",
        "status": "ok"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "visionguard-ai"
    }