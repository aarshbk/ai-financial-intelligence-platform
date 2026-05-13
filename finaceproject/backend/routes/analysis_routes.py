"""
API Routes for Document Analysis
"""
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging

from backend.services import AnalysisService
from backend.models import UploadResponse, DocumentAnalysis, QAQuery, QAResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["analysis"])

# Global service instance
analysis_service = AnalysisService()


@router.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and analyze a financial document
    """
    try:
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"File uploaded: {file.filename}")
        
        # Analyze document
        analysis = analysis_service.analyze_document(file_path)
        
        return {
            "status": "success",
            "message": f"Document '{file.filename}' analyzed successfully",
            "analysis": analysis
        }
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents():
    """
    List all uploaded and analyzed documents
    """
    try:
        documents = analysis_service.list_documents()
        return {
            "status": "success",
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{doc_id}")
async def get_document_summary(doc_id: str):
    """
    Get summary of a specific document
    """
    try:
        summary = analysis_service.get_document_summary(doc_id)
        return {
            "status": "success",
            "data": summary
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting document summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_documents(doc1_id: str, doc2_id: str):
    """
    Compare two uploaded documents
    """
    try:
        comparison = analysis_service.compare_documents(doc1_id, doc2_id)
        return {
            "status": "success",
            "comparison": comparison
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/question", response_model=dict)
async def ask_question(query: QAQuery):
    """
    Ask a question about uploaded financial documents
    """
    try:
        if not analysis_service.uploaded_documents:
            raise HTTPException(
                status_code=400,
                detail="No documents have been uploaded yet"
            )
        
        response = analysis_service.answer_question(
            query.query,
            use_openai=query.use_openai
        )
        
        return {
            "status": "success",
            "data": response
        }
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{doc_id}")
async def export_analysis(doc_id: str, format: str = "json"):
    """
    Export analysis results
    """
    try:
        result = analysis_service.export_analysis(doc_id, format)
        return {
            "status": "success",
            "format": format,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Financial Intelligence Platform API",
        "version": "1.0.0"
    }
