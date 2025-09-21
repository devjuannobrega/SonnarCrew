"""
CrewAI integration tools and utilities
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CrewTool:
    """
    Tool for CrewAI integration and configuration management
    """

    def __init__(self):
        self.name = "CrewTool"
        self.description = "CrewAI integration and configuration tool"
        self.version = "1.0.0"
        self.config_path = Path(__file__).parent.parent / "config"

    def load_agents_config(self) -> Dict[str, Any]:
        """Load agents configuration from YAML file"""
        # Try multiple possible paths
        possible_paths = [
            self.config_path / "agents.yaml",
            self.config_path.parent / "config" / "agents.yaml",
            Path(__file__).parent.parent / "config" / "agents.yaml"
        ]

        config_file = None
        for path in possible_paths:
            if path.exists():
                config_file = path
                break

        if not config_file:
            logger.error(f"Agents config file not found in any of: {[str(p) for p in possible_paths]}")
            return self._get_default_agents_config()

        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Agents configuration loaded from: {config_file}")
                return config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing agents config: {e}")
            return self._get_default_agents_config()

    def load_tasks_config(self) -> Dict[str, Any]:
        """Load tasks configuration from YAML file"""
        # Try multiple possible paths
        possible_paths = [
            self.config_path / "tasks.yaml",
            self.config_path.parent / "config" / "tasks.yaml",
            Path(__file__).parent.parent / "config" / "tasks.yaml"
        ]

        config_file = None
        for path in possible_paths:
            if path.exists():
                config_file = path
                break

        if not config_file:
            logger.error(f"Tasks config file not found in any of: {[str(p) for p in possible_paths]}")
            return self._get_default_tasks_config()

        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Tasks configuration loaded from: {config_file}")
                return config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing tasks config: {e}")
            return self._get_default_tasks_config()

    def validate_agent_config(self, agent_name: str, config: Dict[str, Any]) -> bool:
        """Validate agent configuration"""
        required_fields = ['name', 'role', 'goal', 'backstory']

        if agent_name not in config.get('agents', {}):
            logger.error(f"Agent {agent_name} not found in configuration")
            return False

        agent_config = config['agents'][agent_name]

        for field in required_fields:
            if field not in agent_config:
                logger.error(f"Missing required field '{field}' in agent {agent_name}")
                return False

        logger.info(f"Agent {agent_name} configuration is valid")
        return True

    def validate_task_config(self, task_name: str, config: Dict[str, Any]) -> bool:
        """Validate task configuration"""
        required_fields = ['name', 'description', 'expected_output', 'agent']

        if task_name not in config.get('tasks', {}):
            logger.error(f"Task {task_name} not found in configuration")
            return False

        task_config = config['tasks'][task_name]

        for field in required_fields:
            if field not in task_config:
                logger.error(f"Missing required field '{field}' in task {task_name}")
                return False

        logger.info(f"Task {task_name} configuration is valid")
        return True

    def get_agent_by_name(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration by name"""
        config = self.load_agents_config()
        return config.get('agents', {}).get(agent_name)

    def get_task_by_name(self, task_name: str) -> Optional[Dict[str, Any]]:
        """Get task configuration by name"""
        config = self.load_tasks_config()
        return config.get('tasks', {}).get(task_name)

    def get_workflow_by_name(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get workflow configuration by name"""
        config = self.load_tasks_config()
        return config.get('workflows', {}).get(workflow_name)

    def create_agent_instance(self, agent_name: str) -> Dict[str, Any]:
        """Create an agent instance with configuration"""
        agent_config = self.get_agent_by_name(agent_name)
        if not agent_config:
            raise ValueError(f"Agent {agent_name} not found")

        return {
            "name": agent_config["name"],
            "role": agent_config["role"],
            "goal": agent_config["goal"],
            "backstory": agent_config["backstory"],
            "capabilities": agent_config.get("capabilities", []),
            "tools": agent_config.get("tools", []),
            "verbose": agent_config.get("verbose", True),
            "memory": agent_config.get("memory", True),
            "max_iter": agent_config.get("max_iter", 5),
            "max_execution_time": agent_config.get("max_execution_time", 60)
        }

    def create_task_instance(self, task_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a task instance with configuration"""
        task_config = self.get_task_by_name(task_name)
        if not task_config:
            raise ValueError(f"Task {task_name} not found")

        task_instance = {
            "name": task_config["name"],
            "description": task_config["description"],
            "expected_output": task_config["expected_output"],
            "agent": task_config["agent"],
            "priority": task_config.get("priority", "medium"),
            "dependencies": task_config.get("dependencies", []),
            "tools_required": task_config.get("tools_required", []),
            "timeout": task_config.get("timeout", 60),
            "retry_count": task_config.get("retry_count", 1),
            "created_at": datetime.now(),
            "context": context or {}
        }

        return task_instance

    def execute_workflow(self, workflow_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a workflow with the given context"""
        workflow_config = self.get_workflow_by_name(workflow_name)
        if not workflow_config:
            raise ValueError(f"Workflow {workflow_name} not found")

        workflow_result = {
            "workflow_name": workflow_name,
            "started_at": datetime.now(),
            "tasks": [],
            "status": "running",
            "context": context or {}
        }

        try:
            for task_name in workflow_config["tasks"]:
                task_instance = self.create_task_instance(task_name, context)
                task_result = self._simulate_task_execution(task_instance)
                workflow_result["tasks"].append(task_result)

                # Update context with task results
                if task_result["status"] == "completed":
                    workflow_result["context"].update(task_result.get("output", {}))
                elif workflow_config.get("failure_strategy") == "stop_on_first_failure":
                    workflow_result["status"] = "failed"
                    workflow_result["error"] = f"Task {task_name} failed"
                    break

            if workflow_result["status"] == "running":
                workflow_result["status"] = "completed"

        except Exception as e:
            workflow_result["status"] = "failed"
            workflow_result["error"] = str(e)

        workflow_result["completed_at"] = datetime.now()
        workflow_result["execution_time"] = (
            workflow_result["completed_at"] - workflow_result["started_at"]
        ).total_seconds()

        return workflow_result

    def _simulate_task_execution(self, task_instance: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate task execution (placeholder for actual CrewAI integration)"""
        return {
            "task_name": task_instance["name"],
            "agent": task_instance["agent"],
            "status": "completed",
            "started_at": datetime.now(),
            "completed_at": datetime.now(),
            "execution_time": 1.0,
            "output": {
                "message": f"Task {task_instance['name']} executed successfully",
                "agent_used": task_instance["agent"]
            }
        }

    def _get_default_agents_config(self) -> Dict[str, Any]:
        """Get default agents configuration if file is not available"""
        return {
            "agents": {
                "analisador_codigo": {
                    "name": "Agente Analisador de Código",
                    "role": "Especialista em Análise de Código Python",
                    "goal": "Analisar código Python para identificar oportunidades de otimização",
                    "backstory": "Desenvolvedor Python experiente com foco em qualidade de código",
                    "capabilities": ["analise_sintaxe", "analise_performance"],
                    "tools": ["analisador_ast", "calculador_complexidade"],
                    "verbose": True,
                    "memory": True,
                    "max_iter": 3,
                    "max_execution_time": 30
                }
            }
        }

    def _get_default_tasks_config(self) -> Dict[str, Any]:
        """Get default tasks configuration if file is not available"""
        return {
            "tasks": {
                "tarefa_analise_codigo": {
                    "name": "Análise de Código Python",
                    "description": "Analisar código Python para identificar problemas",
                    "expected_output": "Relatório de análise com sugestões",
                    "agent": "analisador_codigo",
                    "priority": "alta",
                    "timeout": 30
                }
            },
            "workflows": {
                "analise_completa": {
                    "name": "Fluxo de Análise Completa de Código",
                    "tasks": ["tarefa_analise_codigo"],
                    "execution_mode": "sequencial"
                }
            }
        }

    def get_crew_status(self) -> Dict[str, Any]:
        """Get status of the crew configuration"""
        agents_config = self.load_agents_config()
        tasks_config = self.load_tasks_config()

        return {
            "agents_count": len(agents_config.get("agents", {})),
            "tasks_count": len(tasks_config.get("tasks", {})),
            "workflows_count": len(tasks_config.get("workflows", {})),
            "config_valid": True,
            "last_updated": datetime.now()
        }