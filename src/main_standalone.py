
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.code_analyzer_agent import CodeAnalyzerAgent
from src.models.analysis import AnalysisRequest, AnalysisResponse, AnalysisMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Code Analysis Agent API (Standalone)",
    description="Agent for Python code analysis without database dependency",
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

# In-memory storage for testing
analysis_history = []
analysis_counter = 0

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "mode": "standalone"}

@app.post("/analyze-code", response_model=AnalysisResponse)
async def analyze_code(request: AnalysisRequest):
    """
    Analyze Python code and return optimization suggestions
    """
    global analysis_counter

    try:
        # Validate input
        if not request.code_snippet.strip():
            raise HTTPException(status_code=400, detail="Code snippet cannot be empty")

        # Create agent and analyze
        agent = CodeAnalyzerAgent()
        analysis_result = await agent.analyze_code(request.code_snippet)

        # Create response
        analysis_counter += 1

        response = AnalysisResponse(
            analysis_id=analysis_counter,
            suggestions=analysis_result.get("suggestions", []),
            metrics=AnalysisMetrics(**analysis_result.get("metrics", {})),
            processing_time_ms=analysis_result.get("processing_time_ms", 0),
            timestamp=datetime.now(),
            agent_version="1.0.0",
            summary=analysis_result.get("summary", "Analysis completed")
        )

        # Store in memory
        analysis_history.append({
            "id": analysis_counter,
            "code_snippet": request.code_snippet[:200] + "..." if len(request.code_snippet) > 200 else request.code_snippet,
            "suggestions_count": len(response.suggestions),
            "created_at": response.timestamp,
            "summary": response.summary
        })

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")

@app.get("/analysis-history")
async def get_analysis_history(limit: int = 10, offset: int = 0):
    """
    Get analysis history with pagination (from memory)
    """
    try:
        start = max(0, len(analysis_history) - limit - offset)
        end = len(analysis_history) - offset if offset > 0 else len(analysis_history)

        history_slice = analysis_history[start:end]
        history_slice.reverse()  # Most recent first

        return {"history": history_slice, "total": len(analysis_history)}

    except Exception as e:
        logger.error(f"Error fetching analysis history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/agent-status")
async def get_agent_status():
    """
    Get agent status information
    """
    try:
        return {
            "status": "healthy",
            "version": "1.0.0-standalone",
            "mode": "standalone (no database)",
            "total_analyses": len(analysis_history),
            "uptime": "running",
            "features": {
                "database": False,
                "yaml_config": True,
                "code_analysis": True
            }
        }

    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/config-info")
async def get_config_info():
    """
    Get information about loaded configurations
    """
    try:
        from src.tools.crew import CrewTool

        crew_tool = CrewTool()
        agents_config = crew_tool.load_agents_config()
        tasks_config = crew_tool.load_tasks_config()

        return {
            "agents_config": {
                "loaded": len(agents_config.get("agents", {})) > 0,
                "agents_count": len(agents_config.get("agents", {})),
                "agents": list(agents_config.get("agents", {}).keys())
            },
            "tasks_config": {
                "loaded": len(tasks_config.get("tasks", {})) > 0,
                "tasks_count": len(tasks_config.get("tasks", {})),
                "workflows_count": len(tasks_config.get("workflows", {})),
                "tasks": list(tasks_config.get("tasks", {}).keys()),
                "workflows": list(tasks_config.get("workflows", {}).keys())
            },
            "mode": "standalone"
        }

    except Exception as e:
        logger.error(f"Error getting config info: {e}")
        return {
            "agents_config": {"loaded": False, "error": str(e)},
            "tasks_config": {"loaded": False, "error": str(e)},
            "mode": "standalone"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
