from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from app.backend.services.rag_service import RAGService
from app.backend.services.vlm_service import VLMService
from app.backend.services.report_service import InspectionPipelineService


router = APIRouter(prefix="/inspection", tags=["Inspection"])

rag_service = RAGService()
vlm_service = VLMService()
inspection_pipeline_service = InspectionPipelineService()


class RuleSearchRequest(BaseModel):
    query: str
    top_k: int = 3


@router.post("/search-rules")
def search_rules(request: RuleSearchRequest):
    results = rag_service.retrieve_rules(
        query=request.query,
        top_k=request.top_k
    )

    return {
        "query": request.query,
        "top_k": request.top_k,
        "results": results
    }


@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    analysis = vlm_service.analyze_image(
        image_bytes=image_bytes,
        filename=file.filename or "uploaded_image.jpg"
    )

    return {
        "filename": file.filename,
        "analysis": analysis.model_dump()
    }


@router.post("/analyze-with-rules")
async def analyze_with_rules(
    file: UploadFile = File(...),
    top_k: int = 3
):
    image_bytes = await file.read()

    result = inspection_pipeline_service.analyze_image_with_rules(
        image_bytes=image_bytes,
        filename=file.filename or "uploaded_image.jpg",
        top_k=top_k
    )

    return {
        "status": "success",
        "result": result
    }


@router.post("/generate-report")
async def generate_report(
    file: UploadFile = File(...),
    top_k: int = 3
):
    image_bytes = await file.read()

    result = inspection_pipeline_service.generate_full_inspection_report(
        image_bytes=image_bytes,
        filename=file.filename or "uploaded_image.jpg",
        top_k=top_k
    )

    return {
        "status": "success",
        "result": result
    }