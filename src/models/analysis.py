from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    """Severity levels for code analysis suggestions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SuggestionCategory(str, Enum):
    """Categories for code suggestions"""
    PERFORMANCE = "performance"
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    BEST_PRACTICES = "best_practices"
    IMPORTS = "imports"
    NAMING = "naming"
    COMPLEXITY = "complexity"

class CodeSuggestion(BaseModel):
    """Individual code suggestion model"""
    line_number: Optional[int] = Field(None, description="Line number where issue occurs")
    category: SuggestionCategory = Field(..., description="Category of the suggestion")
    severity: SeverityLevel = Field(..., description="Severity level of the issue")
    message: str = Field(..., description="Description of the suggestion")
    suggested_fix: Optional[str] = Field(None, description="Suggested code fix")
    rule_name: str = Field(..., description="Name of the rule that triggered this suggestion")

class AnalysisRequest(BaseModel):
    """Request model for code analysis"""
    code_snippet: str = Field(..., min_length=1, description="Python code to analyze")
    include_performance_analysis: bool = Field(True, description="Include performance suggestions")
    include_security_analysis: bool = Field(True, description="Include security suggestions")
    max_suggestions: int = Field(20, ge=1, le=100, description="Maximum number of suggestions")

    @validator('code_snippet')
    def validate_code_snippet(cls, v):
        if not v.strip():
            raise ValueError('Code snippet cannot be empty')
        return v.strip()

class AnalysisMetrics(BaseModel):
    """Metrics about the analyzed code"""
    lines_of_code: int = Field(..., description="Total lines of code")
    cyclomatic_complexity: Optional[int] = Field(None, description="Cyclomatic complexity score")
    maintainability_index: Optional[float] = Field(None, description="Maintainability index (0-100)")
    code_coverage_estimate: Optional[float] = Field(None, description="Estimated testability score")

class AnalysisResponse(BaseModel):
    """Response model for code analysis"""
    analysis_id: Optional[int] = Field(None, description="Database ID of the analysis")
    suggestions: List[CodeSuggestion] = Field(..., description="List of code suggestions")
    metrics: AnalysisMetrics = Field(..., description="Code metrics")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    agent_version: str = Field("1.0.0", description="Version of the analysis agent")
    summary: str = Field(..., description="Summary of the analysis")

class AnalysisHistoryItem(BaseModel):
    """Model for analysis history items"""
    id: int = Field(..., description="Database ID")
    code_snippet: str = Field(..., description="Analyzed code snippet")
    suggestions_count: int = Field(..., description="Number of suggestions generated")
    created_at: datetime = Field(..., description="Analysis creation timestamp")
    processing_time: Optional[int] = Field(None, description="Processing time in milliseconds")
    summary: str = Field(..., description="Brief summary of the analysis")

class AgentStatus(BaseModel):
    """Model for agent status information"""
    status: str = Field(..., description="Agent status")
    version: str = Field(..., description="Agent version")
    uptime: str = Field(..., description="Agent uptime")
    total_analyses: int = Field(..., description="Total number of analyses performed")
    average_processing_time: float = Field(..., description="Average processing time in ms")
    last_analysis: Optional[datetime] = Field(None, description="Timestamp of last analysis")

class CrewTaskResult(BaseModel):
    """Model for CrewAI task results"""
    task_id: str = Field(..., description="Task identifier")
    agent_name: str = Field(..., description="Name of the agent that executed the task")
    status: str = Field(..., description="Task execution status")
    result: Dict[str, Any] = Field(..., description="Task execution result")
    execution_time: float = Field(..., description="Task execution time in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")