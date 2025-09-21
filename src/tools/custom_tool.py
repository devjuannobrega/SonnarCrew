"""
Custom tools for code analysis agents
"""

import ast
import re
import hashlib
from typing import Dict, Any, List


class CustomAnalysisTool:
    """
    Custom tool for advanced code analysis operations
    """

    def __init__(self):
        self.name = "CustomAnalysisTool"
        self.description = "Advanced Python code analysis tool"
        self.version = "1.0.0"

    def calculate_code_hash(self, code: str) -> str:
        """Calculate hash of the code for caching purposes"""
        return hashlib.md5(code.encode()).hexdigest()

    def extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract function information from code"""
        functions = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line_number": node.lineno,
                        "args_count": len(node.args.args),
                        "has_docstring": ast.get_docstring(node) is not None,
                        "is_async": isinstance(node, ast.AsyncFunctionDef)
                    })
        except SyntaxError:
            pass
        return functions

    def extract_classes(self, code: str) -> List[Dict[str, Any]]:
        """Extract class information from code"""
        classes = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [
                        n.name for n in node.body
                        if isinstance(n, ast.FunctionDef)
                    ]
                    classes.append({
                        "name": node.name,
                        "line_number": node.lineno,
                        "methods": methods,
                        "method_count": len(methods),
                        "has_docstring": ast.get_docstring(node) is not None
                    })
        except SyntaxError:
            pass
        return classes

    def extract_imports(self, code: str) -> Dict[str, List[str]]:
        """Extract import information from code"""
        imports = {
            "standard": [],
            "third_party": [],
            "local": []
        }

        # Standard library modules (simplified list)
        standard_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'math', 're',
            'collections', 'itertools', 'functools', 'operator',
            'typing', 'pathlib', 'urllib', 'http', 'asyncio'
        }

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        if module_name in standard_modules:
                            imports["standard"].append(alias.name)
                        else:
                            imports["third_party"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        if module_name in standard_modules:
                            imports["standard"].append(node.module)
                        elif module_name.startswith('.'):
                            imports["local"].append(node.module)
                        else:
                            imports["third_party"].append(node.module)
        except SyntaxError:
            pass

        return imports

    def detect_code_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Detect common code patterns and anti-patterns"""
        patterns = []
        lines = code.split('\n')

        # Pattern 1: Long parameter lists
        for i, line in enumerate(lines, 1):
            if 'def ' in line:
                # Count parameters (simple regex approach)
                param_match = re.search(r'def\s+\w+\s*\((.*?)\)', line)
                if param_match:
                    params = [p.strip() for p in param_match.group(1).split(',') if p.strip()]
                    if len(params) > 5:
                        patterns.append({
                            "pattern": "long_parameter_list",
                            "line": i,
                            "severity": "medium",
                            "message": f"Function has {len(params)} parameters"
                        })

        # Pattern 2: Nested loops
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    nested_loops = 0
                    for child in ast.walk(node):
                        if isinstance(child, (ast.For, ast.While)) and child != node:
                            nested_loops += 1

                    if nested_loops >= 2:
                        patterns.append({
                            "pattern": "deeply_nested_loops",
                            "line": node.lineno,
                            "severity": "high",
                            "message": f"Found {nested_loops + 1} nested loops"
                        })
        except SyntaxError:
            pass

        # Pattern 3: Magic numbers
        magic_number_pattern = re.compile(r'\b(?<![\w.])\d{2,}\b(?![\w.])')
        for i, line in enumerate(lines, 1):
            if magic_number_pattern.search(line):
                patterns.append({
                    "pattern": "magic_numbers",
                    "line": i,
                    "severity": "low",
                    "message": "Consider using named constants instead of magic numbers"
                })

        return patterns

    def calculate_maintainability_score(self, code: str) -> float:
        """Calculate a maintainability score for the code"""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0

        score = 100.0
        lines = len([line for line in code.split('\n') if line.strip()])

        # Deduct points for various factors
        functions = self.extract_functions(code)
        classes = self.extract_classes(code)

        # Long files
        if lines > 300:
            score -= (lines - 300) * 0.1

        # Functions without docstrings
        undocumented_functions = sum(1 for f in functions if not f["has_docstring"])
        score -= undocumented_functions * 2

        # Classes without docstrings
        undocumented_classes = sum(1 for c in classes if not c["has_docstring"])
        score -= undocumented_classes * 3

        # Complex functions (many parameters)
        complex_functions = sum(1 for f in functions if f["args_count"] > 5)
        score -= complex_functions * 5

        return max(0.0, min(100.0, score))

    def suggest_refactoring_opportunities(self, code: str) -> List[Dict[str, Any]]:
        """Suggest refactoring opportunities"""
        suggestions = []
        functions = self.extract_functions(code)

        # Large functions (estimate by line count)
        lines = code.split('\n')
        current_function = None
        function_lines = {}

        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                current_function = line.strip().split('(')[0].replace('def ', '')
                function_lines[current_function] = 1
            elif current_function and (line.startswith('    ') or line.strip() == ''):
                function_lines[current_function] = function_lines.get(current_function, 0) + 1
            elif current_function and not line.startswith('    ') and line.strip():
                current_function = None

        for func_name, line_count in function_lines.items():
            if line_count > 20:
                suggestions.append({
                    "type": "extract_method",
                    "target": func_name,
                    "reason": f"Function is {line_count} lines long, consider breaking it down",
                    "priority": "medium" if line_count < 40 else "high"
                })

        return suggestions

    def analyze_complexity_metrics(self, code: str) -> Dict[str, Any]:
        """Analyze various complexity metrics"""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"error": "Syntax error in code"}

        metrics = {
            "lines_of_code": len([line for line in code.split('\n') if line.strip()]),
            "functions_count": len(self.extract_functions(code)),
            "classes_count": len(self.extract_classes(code)),
            "imports_count": sum(len(imports) for imports in self.extract_imports(code).values()),
            "complexity_score": self._calculate_complexity_score(tree),
            "maintainability_score": self.calculate_maintainability_score(code)
        }

        return metrics

    def _calculate_complexity_score(self, tree: ast.AST) -> int:
        """Calculate overall complexity score"""
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                # Add complexity for each function
                complexity += 1
            elif isinstance(node, ast.ClassDef):
                # Add complexity for each class
                complexity += 2

        return complexity