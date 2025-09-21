from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio
from datetime import datetime
import logging

from src.agents.code_analyzer_agent import CodeAnalyzerAgent
from src.database.database import get_db_session, create_tables
from src.models.analysis import AnalysisRequest, AnalysisResponse
from src.services.analysis_service import AnalysisService
from src.crew.orchestrator import CrewOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Code Analysis Agent API",
    description="Agent for Python code analysis and optimization suggestions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analysis_service = AnalysisService()
crew_orchestrator = CrewOrchestrator()


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/analyze-code", response_model=AnalysisResponse)
async def analyze_code(
        request: AnalysisRequest,
        db_session=Depends(get_db_session)
):
    """
    Analyze Python code and return optimization suggestions
    """
    try:
        # Validate input
        if not request.code_snippet.strip():
            raise HTTPException(status_code=400, detail="Code snippet cannot be empty")

        # Process analysis through CrewAI orchestration
        analysis_result = await crew_orchestrator.orchestrate_analysis(
            code_snippet=request.code_snippet,
            db_session=db_session
        )

        return analysis_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")


@app.get("/analysis-history")
async def get_analysis_history(
        limit: int = 10,
        offset: int = 0,
        db_session=Depends(get_db_session)
):
    """
    Get analysis history with pagination
    """
    try:
        history = await analysis_service.get_analysis_history(
            db_session, limit=limit, offset=offset
        )
        return {"history": history}

    except Exception as e:
        logger.error(f"Error fetching analysis history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/agent-status")
async def get_agent_status():
    """
    Get detailed agent status information
    """
    try:
        status = await crew_orchestrator.get_orchestrator_status()
        return status

    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/config-info")
async def get_config_info():
    """
    Get information about loaded YAML configurations
    """
    try:
        config_info = crew_orchestrator.get_configuration_info()
        return config_info

    except Exception as e:
        logger.error(f"Error getting config info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)