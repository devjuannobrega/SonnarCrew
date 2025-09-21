import ast
import re
import time
from typing import List, Dict, Any, Optional
import logging

from src.models.analysis import (
    CodeSuggestion, 
    SeverityLevel, 
    SuggestionCategory,
    AnalysisMetrics,
)

logger = logging.getLogger(__name__)

class CodeAnalyzerAgent:
    """
    Agent responsible for analyzing Python code and providing optimization suggestions
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.name = "CodeAnalyzer"
        self.description = "Python code analysis and optimization agent"
    
    async def analyze_code(self, code_snippet: str) -> Dict[str, Any]:
        """
        Main method to analyze Python code and return suggestions
        """
        start_time = time.time()
        
        try:
            # Parse the code
            try:
                tree = ast.parse(code_snippet)
            except SyntaxError as e:
                return {
                    "suggestions": [{
                        "line_number": e.lineno,
                        "category": SuggestionCategory.BEST_PRACTICES,
                        "severity": SeverityLevel.CRITICAL,
                        "message": f"Syntax error: {e.msg}",
                        "suggested_fix": "Fix the syntax error",
                        "rule_name": "syntax_check"
                    }],
                    "metrics": self._calculate_basic_metrics(code_snippet),
                    "processing_time_ms": int((time.time() - start_time) * 1000),
                    "summary": "Code contains syntax errors that must be fixed."
                }
            
            # Perform various analyses
            suggestions = []
            
            # 1. Import analysis
            suggestions.extend(self._analyze_imports(tree, code_snippet))
            
            # 2. Naming conventions
            suggestions.extend(self._analyze_naming_conventions(tree))
            
            # 3. Code complexity
            suggestions.extend(self._analyze_complexity(tree))
            
            # 4. Performance issues
            suggestions.extend(self._analyze_performance(tree, code_snippet))
            
            # 5. Security issues
            suggestions.extend(self._analyze_security(tree, code_snippet))
            
            # 6. Best practices
            suggestions.extend(self._analyze_best_practices(tree, code_snippet))
            
            # Calculate metrics
            metrics = self._calculate_metrics(tree, code_snippet)
            
            # Generate summary
            summary = self._generate_summary(suggestions, metrics)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "suggestions": [suggestion.dict() for suggestion in suggestions],
                "metrics": metrics.dict(),
                "processing_time_ms": processing_time,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error during code analysis: {e}")
            return {
                "suggestions": [{
                    "line_number": None,
                    "category": SuggestionCategory.BEST_PRACTICES,
                    "severity": SeverityLevel.HIGH,
                    "message": f"Analysis failed: {str(e)}",
                    "suggested_fix": "Please check your code for issues",
                    "rule_name": "analysis_error"
                }],
                "metrics": self._calculate_basic_metrics(code_snippet),
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "summary": "Code analysis encountered errors."
            }
    
    def _analyze_imports(self, tree: ast.AST, code: str) -> List[CodeSuggestion]:
        """Analyze import statements"""
        suggestions = []
        imports_found = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports_found.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports_found.append((node.module, node.lineno))
        
        # Check for unused imports (basic check)
        code_without_imports = '\n'.join([
            line for line in code.split('\n') 
            if not line.strip().startswith('import') and not line.strip().startswith('from')
        ])
        
        for import_name, line_no in imports_found:
            base_name = import_name.split('.')[0]
            if base_name not in code_without_imports:
                suggestions.append(CodeSuggestion(
                    line_number=line_no,
                    category=SuggestionCategory.IMPORTS,
                    severity=SeverityLevel.LOW,
                    message=f"Import '{import_name}' appears to be unused",
                    suggested_fix=f"Remove unused import: {import_name}",
                    rule_name="unused_import"
                ))
        
        return suggestions
    
    def _analyze_naming_conventions(self, tree: ast.AST) -> List[CodeSuggestion]:
        """Analyze naming conventions"""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    suggestions.append(CodeSuggestion(
                        line_number=node.lineno,
                        category=SuggestionCategory.NAMING,
                        severity=SeverityLevel.MEDIUM,
                        message=f"Function name '{node.name}' doesn't follow snake_case convention",
                        suggested_fix=f"Rename to follow snake_case: {self._to_snake_case(node.name)}",
                        rule_name="function_naming"
                    ))
            
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    suggestions.append(CodeSuggestion(
                        line_number=node.lineno,
                        category=SuggestionCategory.NAMING,
                        severity=SeverityLevel.MEDIUM,
                        message=f"Class name '{node.name}' doesn't follow PascalCase convention",
                        suggested_fix=f"Rename to follow PascalCase",
                        rule_name="class_naming"
                    ))
        
        return suggestions
    
    def _analyze_complexity(self, tree: ast.AST) -> List[CodeSuggestion]:
        """Analyze code complexity"""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    suggestions.append(CodeSuggestion(
                        line_number=node.lineno,
                        category=SuggestionCategory.COMPLEXITY,
                        severity=SeverityLevel.HIGH if complexity > 15 else SeverityLevel.MEDIUM,
                        message=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                        suggested_fix="Consider breaking this function into smaller functions",
                        rule_name="high_complexity"
                    ))
                
                # Check for too many parameters
                if len(node.args.args) > 5:
                    suggestions.append(CodeSuggestion(
                        line_number=node.lineno,
                        category=SuggestionCategory.MAINTAINABILITY,
                        severity=SeverityLevel.MEDIUM,
                        message=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                        suggested_fix="Consider using a configuration object or reducing parameters",
                        rule_name="too_many_parameters"
                    ))
        
        return suggestions
    
    def _analyze_performance(self, tree: ast.AST, code: str) -> List[CodeSuggestion]:
        """Analyze performance issues"""
        suggestions = []
        
        for node in ast.walk(tree):
            # Check for inefficient loops
            if isinstance(node, ast.For):
                # Check for list concatenation in loops
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        suggestions.append(CodeSuggestion(
                            line_number=node.lineno,
                            category=SuggestionCategory.PERFORMANCE,
                            severity=SeverityLevel.MEDIUM,
                            message="Avoid list concatenation in loops",
                            suggested_fix="Use list.extend() or list comprehension instead",
                            rule_name="inefficient_loop_concatenation"
                        ))
            
            # Check for global variable usage
            if isinstance(node, ast.Global):
                suggestions.append(CodeSuggestion(
                    line_number=node.lineno,
                    category=SuggestionCategory.PERFORMANCE,
                    severity=SeverityLevel.LOW,
                    message="Global variables can impact performance and maintainability",
                    suggested_fix="Consider passing variables as parameters or using class attributes",
                    rule_name="global_variable_usage"
                ))
        
        return suggestions
    
    def _analyze_security(self, tree: ast.AST, code: str) -> List[CodeSuggestion]:
        """Analyze security issues"""
        suggestions = []
        
        # Check for eval() usage
        if 'eval(' in code:
            suggestions.append(CodeSuggestion(
                line_number=None,
                category=SuggestionCategory.SECURITY,
                severity=SeverityLevel.CRITICAL,
                message="Usage of eval() poses security risks",
                suggested_fix="Use ast.literal_eval() for safe evaluation or find alternative approaches",
                rule_name="eval_usage"
            ))
        
        # Check for exec() usage
        if 'exec(' in code:
            suggestions.append(CodeSuggestion(
                line_number=None,
                category=SuggestionCategory.SECURITY,
                severity=SeverityLevel.CRITICAL,
                message="Usage of exec() poses security risks",
                suggested_fix="Avoid exec() or ensure input is properly sanitized",
                rule_name="exec_usage"
            ))
        
        return suggestions
    
    def _analyze_best_practices(self, tree: ast.AST, code: str) -> List[CodeSuggestion]:
        """Analyze best practices"""
        suggestions = []
        lines = code.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 88:  # PEP 8 recommends 79, but 88 is acceptable
                suggestions.append(CodeSuggestion(
                    line_number=i,
                    category=SuggestionCategory.READABILITY,
                    severity=SeverityLevel.LOW,
                    message=f"Line too long ({len(line)} characters)",
                    suggested_fix="Break long lines using parentheses or line continuation",
                    rule_name="line_too_long"
                ))
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    suggestions.append(CodeSuggestion(
                        line_number=node.lineno,
                        category=SuggestionCategory.MAINTAINABILITY,
                        severity=SeverityLevel.LOW,
                        message=f"{node.__class__.__name__.lower().replace('def', '')} '{node.name}' missing docstring",
                        suggested_fix="Add a descriptive docstring",
                        rule_name="missing_docstring"
                    ))
        
        return suggestions
    
    def _calculate_metrics(self, tree: ast.AST, code: str) -> AnalysisMetrics:
        """Calculate code metrics"""
        lines = [line for line in code.split('\n') if line.strip()]
        
        return AnalysisMetrics(
            lines_of_code=len(lines),
            cyclomatic_complexity=self._calculate_overall_complexity(tree),
            maintainability_index=self._calculate_maintainability_index(tree, code),
            code_coverage_estimate=self._estimate_testability(tree)
        )
    
    def _calculate_basic_metrics(self, code: str) -> AnalysisMetrics:
        """Calculate basic metrics for code with syntax errors"""
        lines = [line for line in code.split('\n') if line.strip()]
        
        return AnalysisMetrics(
            lines_of_code=len(lines),
            cyclomatic_complexity=None,
            maintainability_index=None,
            code_coverage_estimate=None
        )
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_overall_complexity(self, tree: ast.AST) -> int:
        """Calculate overall complexity of the code"""
        total_complexity = 0
        function_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_complexity += self._calculate_cyclomatic_complexity(node)
                function_count += 1
        
        return total_complexity if function_count == 0 else total_complexity // function_count
    
    def _calculate_maintainability_index(self, tree: ast.AST, code: str) -> float:
        """Calculate a simple maintainability index"""
        lines = len([line for line in code.split('\n') if line.strip()])
        complexity = self._calculate_overall_complexity(tree)
        
        if lines == 0:
            return 100.0
        
        # Simplified maintainability index
        mi = max(0, 100 - (complexity * 2) - (lines * 0.1))
        return round(mi, 2)
    
    def _estimate_testability(self, tree: ast.AST) -> float:
        """Estimate how testable the code is"""
        function_count = 0
        complex_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_count += 1
                if self._calculate_cyclomatic_complexity(node) > 5:
                    complex_functions += 1
        
        if function_count == 0:
            return 50.0
        
        testability = 100 - ((complex_functions / function_count) * 50)
        return round(testability, 2)
    
    def _generate_summary(self, suggestions: List[CodeSuggestion], metrics: AnalysisMetrics) -> str:
        """Generate a summary of the analysis"""
        if not suggestions:
            return "Code looks good! No major issues found."
        
        critical_count = sum(1 for s in suggestions if s.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for s in suggestions if s.severity == SeverityLevel.HIGH)
        
        if critical_count > 0:
            return f"Found {critical_count} critical issue(s) and {len(suggestions)} total suggestions. Immediate attention required."
        elif high_count > 0:
            return f"Found {high_count} high priority issue(s) and {len(suggestions)} total suggestions. Consider addressing soon."
        else:
            return f"Found {len(suggestions)} suggestions for improvement. Code is generally good."
    
    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    async def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": [
                "Syntax analysis",
                "Import optimization", 
                "Naming convention checks",
                "Complexity analysis",
                "Performance suggestions",
                "Security vulnerability detection",
                "Best practices enforcement"
            ]
        }