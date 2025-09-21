import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.agents.code_analyzer_agent import CodeAnalyzerAgent
from src.models.analysis import AnalysisResponse, AnalysisMetrics, CrewTaskResult, AgentStatus
from src.services.analysis_service import AnalysisService
from src.tools.crew import CrewTool

logger = logging.getLogger(__name__)


class CrewOrchestrator:
    """
    Orchestrates the workflow between different agents following CrewAI pattern
    Uses YAML configuration files for agents and tasks
    """

    def __init__(self):
        # Initialize CrewAI tool for configuration management
        self.crew_tool = CrewTool()

        # Load configurations from YAML files
        self.agents_config = self.crew_tool.load_agents_config()
        self.tasks_config = self.crew_tool.load_tasks_config()

        # Initialize agents based on configuration
        self.agents = self._initialize_agents()
        self.analysis_service = AnalysisService()
        self.start_time = datetime.now()
        self.task_history: List[CrewTaskResult] = []

        logger.info(f"CrewOrchestrator initialized with {len(self.agents)} agents")
        logger.info(f"Available workflows: {list(self.tasks_config.get('workflows', {}).keys())}")

    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize agents based on YAML configuration"""
        agents = {}

        for agent_name, agent_config in self.agents_config.get("agents", {}).items():
            try:
                if agent_name == "analisador_codigo":
                    # Create code analyzer with config
                    agent = CodeAnalyzerAgent()
                    agent.config = agent_config
                    agents[agent_name] = agent
                    logger.info(f"Initialized agent: {agent_config['name']}")

                elif agent_name == "processador_resposta":
                    # Create response processor with config
                    agent = ResponseAgent()
                    agent.config = agent_config
                    agents[agent_name] = agent
                    logger.info(f"Initialized agent: {agent_config['name']}")

                elif agent_name == "salvador_dados":
                    # Create data saver with config
                    agent = SaveAgent()
                    agent.config = agent_config
                    agents[agent_name] = agent
                    logger.info(f"Initialized agent: {agent_config['name']}")

            except Exception as e:
                logger.error(f"Failed to initialize agent {agent_name}: {e}")

        return agents

    async def orchestrate_analysis(
            self,
            code_snippet: str,
            db_session: AsyncSession
    ) -> AnalysisResponse:
        """
        Main orchestration method using YAML workflow configuration
        """
        start_time = time.time()
        task_id = str(uuid.uuid4())

        try:
            logger.info(f"Starting analysis orchestration - Task ID: {task_id}")

            # Get workflow configuration from YAML
            workflow_name = self.tasks_config.get("execution_config", {}).get("default_workflow", "analise_completa")
            workflow_config = self.tasks_config.get("workflows", {}).get(workflow_name, {})

            if not workflow_config:
                logger.error(f"Workflow {workflow_name} not found in configuration")
                raise ValueError(f"Workflow {workflow_name} not configured")

            logger.info(f"Executing workflow: {workflow_config['name']}")

            # Execute tasks according to workflow configuration
            workflow_context = {"code_snippet": code_snippet}
            task_results = []

            for task_name in workflow_config["tasks"]:
                task_config = self.tasks_config.get("tasks", {}).get(task_name)
                if not task_config:
                    logger.error(f"Task {task_name} not found in configuration")
                    continue

                # Execute task based on configuration
                task_result = await self._execute_configured_task(
                    task_name,
                    task_config,
                    workflow_context,
                    db_session
                )

                task_results.append(task_result)

                # Update context with task results - FIXED DATA FLOW
                if task_result["status"] == "completed":
                    result_data = task_result.get("result", {})

                    # Handle different types of results properly
                    if isinstance(result_data, dict):
                        workflow_context.update(result_data)

                elif workflow_config.get("failure_strategy") == "stop_on_first_failure":
                    logger.error(f"Task {task_name} failed, stopping workflow")
                    break

            # Extract final analysis result - IMPROVED EXTRACTION
            analysis_result = None
            analysis_id = None

            for result in task_results:
                if result.get("status") != "completed":
                    continue

                result_data = result.get("result", {})
                task_name_key = result.get("task_id", "")

                # Extract analysis result from the code analysis task
                if "analise" in task_name_key or result.get("agent_name") == "analisador_codigo":
                    analysis_result = result_data

                # Extract analysis ID from save task
                elif "persistencia" in task_name_key or result.get("agent_name") == "salvador_dados":
                    analysis_id = result_data.get("analysis_id")

            if not analysis_result:
                # Fallback: try to find any result with suggestions
                for result in task_results:
                    result_data = result.get("result", {})
                    if isinstance(result_data, dict) and "suggestions" in result_data:
                        analysis_result = result_data
                        break

            if not analysis_result:
                raise ValueError("No valid analysis result found in task execution")

            # Create final response with error handling
            try:
                # Ensure we have the required fields with defaults
                suggestions = analysis_result.get("suggestions", [])
                metrics_data = analysis_result.get("metrics", {})

                # Handle case where suggestions might not be properly structured
                if not isinstance(suggestions, list):
                    suggestions = []

                # Handle case where metrics might not be properly structured
                if not isinstance(metrics_data, dict):
                    metrics_data = {"lines_of_code": len(code_snippet.split('\n'))}

                # Create metrics object
                metrics = AnalysisMetrics(**metrics_data)

                response = AnalysisResponse(
                    analysis_id=analysis_id,
                    suggestions=suggestions,
                    metrics=metrics,
                    processing_time_ms=analysis_result.get("processing_time_ms",
                                                           int((time.time() - start_time) * 1000)),
                    timestamp=datetime.now(),
                    agent_version="1.0.0",
                    summary=analysis_result.get("summary", "Analysis completed successfully")
                )

                logger.info(f"Analysis orchestration completed - Task ID: {task_id}")
                return response

            except Exception as e:
                logger.error(f"Error creating response: {e}")
                # Create minimal response
                return AnalysisResponse(
                    analysis_id=analysis_id,
                    suggestions=[],
                    metrics=AnalysisMetrics(lines_of_code=len(code_snippet.split('\n'))),
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    timestamp=datetime.now(),
                    agent_version="1.0.0",
                    summary=f"Analysis completed with issues: {str(e)}"
                )

        except Exception as e:
            logger.error(f"Error in analysis orchestration: {e}")
            # Return error response
            return AnalysisResponse(
                analysis_id=None,
                suggestions=[],
                metrics=AnalysisMetrics(lines_of_code=len(code_snippet.split('\n'))),
                processing_time_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(),
                agent_version="1.0.0",
                summary=f"Analysis failed: {str(e)}"
            )

    async def _execute_configured_task(
            self,
            task_name: str,
            task_config: Dict[str, Any],
            context: Dict[str, Any],
            db_session: AsyncSession = None
    ) -> CrewTaskResult:
        """Execute a task based on its YAML configuration"""
        start_time = time.time()
        task_id = f"{task_name}_{uuid.uuid4().hex[:8]}"

        try:
            logger.info(f"Executing configured task: {task_config['name']}")

            # Get agent for this task
            agent_name = task_config["agent"]
            agent = self.agents.get(agent_name)

            if not agent:
                raise ValueError(f"Agent {agent_name} not found")

            # Execute task based on agent type
            result = None

            if agent_name == "analisador_codigo":
                result = await agent.analyze_code(context["code_snippet"])

            elif agent_name == "processador_resposta":
                # Get analysis result from context - fix the data structure issue
                analysis_data = context.copy()

                # If context has suggestions as a list, wrap it properly
                if "suggestions" in analysis_data and isinstance(analysis_data["suggestions"], list):
                    # Create a proper structure for response processing
                    analysis_result = {
                        "suggestions": analysis_data["suggestions"],
                        "metrics": analysis_data.get("metrics", {}),
                        "summary": analysis_data.get("summary", ""),
                        "processing_time_ms": analysis_data.get("processing_time_ms", 0)
                    }
                else:
                    analysis_result = analysis_data

                result = await agent.process_response(analysis_result)

            elif agent_name == "salvador_dados":
                # Save analysis to database
                processing_time = context.get("processing_time_ms", 0)
                result = await agent.save_analysis(
                    context["code_snippet"],
                    context,
                    processing_time,
                    db_session,
                    self.analysis_service
                )

            else:
                result = {"message": f"Task {task_name} executed", "agent": agent_name}

            execution_time = time.time() - start_time

            task_result = CrewTaskResult(
                task_id=task_id,
                agent_name=agent_name,
                status="completed",
                result=result if isinstance(result, dict) else {"data": result},
                execution_time=execution_time
            )

            self.task_history.append(task_result)
            logger.info(f"Task {task_name} completed in {execution_time:.2f}s")
            return task_result.dict()

        except Exception as e:
            logger.error(f"Error in task {task_name}: {e}")
            execution_time = time.time() - start_time

            task_result = CrewTaskResult(
                task_id=task_id,
                agent_name=task_config.get("agent", "unknown"),
                status="failed",
                result={"error": str(e)},
                execution_time=execution_time
            )

            self.task_history.append(task_result)
            return task_result.dict()

    async def get_orchestrator_status(self) -> AgentStatus:
        """Get the status of the orchestrator and all agents"""
        try:
            # Get crew status using CrewTool
            crew_status = self.crew_tool.get_crew_status()

            # Get statistics
            uptime = datetime.now() - self.start_time
            total_tasks = len(self.task_history)

            # Calculate average processing time
            if total_tasks > 0:
                total_time = sum(task.execution_time for task in self.task_history)
                avg_time = (total_time / total_tasks) * 1000  # Convert to ms
            else:
                avg_time = 0.0

            # Get last analysis time
            last_analysis = None
            if self.task_history:
                last_analysis = max(task.created_at for task in self.task_history)

            return AgentStatus(
                status="healthy" if crew_status["config_valid"] else "degraded",
                version="1.0.0",
                uptime=str(uptime),
                total_analyses=total_tasks,
                average_processing_time=round(avg_time, 2),
                last_analysis=last_analysis
            )

        except Exception as e:
            logger.error(f"Error getting orchestrator status: {e}")
            return AgentStatus(
                status="error",
                version="1.0.0",
                uptime=str(datetime.now() - self.start_time),
                total_analyses=0,
                average_processing_time=0.0,
                last_analysis=None
            )

    def get_configuration_info(self) -> Dict[str, Any]:
        """Get information about loaded configurations"""
        return {
            "agents_config": {
                "loaded": len(self.agents_config.get("agents", {})) > 0,
                "agents_count": len(self.agents_config.get("agents", {})),
                "agents": list(self.agents_config.get("agents", {}).keys())
            },
            "tasks_config": {
                "loaded": len(self.tasks_config.get("tasks", {})) > 0,
                "tasks_count": len(self.tasks_config.get("tasks", {})),
                "workflows_count": len(self.tasks_config.get("workflows", {})),
                "tasks": list(self.tasks_config.get("tasks", {}).keys()),
                "workflows": list(self.tasks_config.get("workflows", {}).keys())
            }
        }

    async def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent task history"""
        try:
            recent_tasks = sorted(
                self.task_history,
                key=lambda x: x.created_at,
                reverse=True
            )[:limit]

            return [task.dict() for task in recent_tasks]

        except Exception as e:
            logger.error(f"Error getting task history: {e}")
            return []


class ResponseAgent:
    """
    Agent responsible for processing and formatting analysis responses
    """

    def __init__(self):
        self.name = "ResponseAgent"
        self.version = "1.0.0"
        self.config = {}

    async def process_response(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance the analysis response"""
        try:
            logger.info(f"Processing response with keys: {list(analysis_result.keys())}")

            # Ensure analysis_result is a dictionary
            if not isinstance(analysis_result, dict):
                logger.error(f"Expected dict, got {type(analysis_result)}")
                analysis_result = {"data": analysis_result}

            # Add additional metadata and formatting
            processed_result = {
                **analysis_result,
                "agent_metadata": {
                    "processor": self.name,
                    "version": self.version,
                    "processed_at": datetime.now().isoformat()
                }
            }

            # Enhance suggestions with additional context if they exist
            if "suggestions" in processed_result and isinstance(processed_result["suggestions"], list):
                for suggestion in processed_result["suggestions"]:
                    if isinstance(suggestion, dict):
                        suggestion["id"] = str(uuid.uuid4())
                        suggestion["confidence"] = self._calculate_confidence(suggestion)

            return processed_result

        except Exception as e:
            logger.error(f"Error processing response: {e}")
            # Return a safe fallback
            return {
                "original_result": analysis_result,
                "processing_error": str(e),
                "agent_metadata": {
                    "processor": self.name,
                    "version": self.version,
                    "processed_at": datetime.now().isoformat()
                }
            }

    def _calculate_confidence(self, suggestion: Dict[str, Any]) -> float:
        """Calculate confidence score for a suggestion"""
        # Simple confidence calculation based on severity and category
        severity_weights = {
            "critical": 0.95,
            "high": 0.85,
            "medium": 0.75,
            "low": 0.65
        }

        base_confidence = severity_weights.get(
            suggestion.get("severity", "low"),
            0.5
        )

        # Adjust based on rule specificity
        if suggestion.get("line_number"):
            base_confidence += 0.1

        return min(0.99, base_confidence)


class SaveAgent:
    """
    Agent responsible for persisting analysis results
    """

    def __init__(self):
        self.name = "SaveAgent"
        self.version = "1.0.0"
        self.config = {}

    async def save_analysis(
            self,
            code_snippet: str,
            analysis_result: Dict[str, Any],
            processing_time: int,
            db_session: AsyncSession,
            analysis_service: AnalysisService
    ) -> Dict[str, Any]:
        """Save analysis result to database"""
        try:
            logger.info("Saving analysis to database")

            analysis_id = await analysis_service.save_analysis(
                db_session,
                code_snippet,
                analysis_result,
                processing_time
            )

            return {
                "analysis_id": analysis_id,
                "saved_at": datetime.now().isoformat(),
                "agent": self.name,
                "success": True
            }

        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return {
                "analysis_id": None,
                "error": str(e),
                "agent": self.name,
                "success": False
            }