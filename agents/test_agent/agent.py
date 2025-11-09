"""Test Agent for analyzing and improving test coverage."""
import os
import subprocess
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class TestAgent(BaseAgent):
    """Agent responsible for test coverage and quality improvements."""
    
    def __init__(self):
        """Initialize the Test Agent."""
        super().__init__(name="test_agent", target_dir="tests")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze test coverage and quality.
        
        Returns:
            Analysis results with testing recommendations
        """
        analysis_results = {
            "test_files": [],
            "coverage": {},
            "recommendations": []
        }
        
        # Find all test files
        test_files = self._find_test_files()
        analysis_results["test_files"] = test_files
        
        # Analyze test structure
        total_tests = 0
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Count test functions
                    test_count = content.count('def test_')
                    test_count += content.count('async def test_')
                    total_tests += test_count
            except Exception:
                pass
        
        analysis_results["total_tests"] = total_tests
        
        # Try to run coverage if pytest-cov is available
        coverage_data = self._run_coverage()
        if coverage_data:
            analysis_results["coverage"] = coverage_data
        
        # Analyze source files vs test files
        source_files = self._get_source_files()
        tested_modules = self._get_tested_modules(test_files)
        
        untested_modules = []
        for source_file in source_files:
            module_name = os.path.basename(source_file).replace('.py', '')
            if module_name not in tested_modules and module_name != '__init__':
                untested_modules.append(source_file)
        
        analysis_results["untested_modules"] = untested_modules
        
        # Recommendations
        if total_tests == 0:
            analysis_results["recommendations"].append({
                "type": "critical",
                "message": "No tests found. Create comprehensive test suite.",
                "priority": "critical"
            })
        elif total_tests < 10:
            analysis_results["recommendations"].append({
                "type": "coverage",
                "message": f"Only {total_tests} tests found. Increase test coverage.",
                "priority": "high"
            })
        
        if len(untested_modules) > 0:
            analysis_results["recommendations"].append({
                "type": "coverage",
                "message": f"{len(untested_modules)} modules have no tests",
                "priority": "high",
                "modules": untested_modules[:5]  # Show first 5
            })
        
        # Check for test types
        has_unit_tests = any('unit' in f.lower() for f in test_files)
        has_integration_tests = any('integration' in f.lower() for f in test_files)
        has_e2e_tests = any('e2e' in f.lower() or 'end_to_end' in f.lower() for f in test_files)
        
        if not has_unit_tests:
            analysis_results["recommendations"].append({
                "type": "test_types",
                "message": "Add unit tests for individual components",
                "priority": "high"
            })
        
        if not has_integration_tests:
            analysis_results["recommendations"].append({
                "type": "test_types",
                "message": "Add integration tests for API endpoints",
                "priority": "medium"
            })
        
        return analysis_results
    
    def _find_test_files(self) -> List[str]:
        """Find all test files in the project."""
        test_files = []
        
        # Check tests directory
        if os.path.exists(self.target_dir):
            for root, dirs, files in os.walk(self.target_dir):
                for file in files:
                    if file.startswith('test_') and file.endswith('.py'):
                        test_files.append(os.path.join(root, file))
        
        # Also check for tests in other directories
        for root, dirs, files in os.walk('.'):
            # Skip venv and hidden directories
            if 'venv' in root or '/.git' in root or '__pycache__' in root:
                continue
            
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    if full_path not in test_files:
                        test_files.append(full_path)
        
        return test_files
    
    def _get_source_files(self) -> List[str]:
        """Get all source Python files."""
        source_files = []
        
        for directory in ['backend', 'frontend', 'agents']:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    # Skip __pycache__
                    if '__pycache__' in root:
                        continue
                    
                    for file in files:
                        if file.endswith('.py'):
                            source_files.append(os.path.join(root, file))
        
        return source_files
    
    def _get_tested_modules(self, test_files: List[str]) -> List[str]:
        """Extract module names that are being tested."""
        tested_modules = []
        
        for test_file in test_files:
            # Extract module name from test file name
            # e.g., test_auth.py -> auth
            basename = os.path.basename(test_file)
            if basename.startswith('test_'):
                module_name = basename[5:].replace('.py', '')
                tested_modules.append(module_name)
        
        return tested_modules
    
    def _run_coverage(self) -> Dict[str, Any]:
        """Run test coverage analysis."""
        try:
            # Try to run pytest with coverage
            result = subprocess.run(
                ['python', '-m', 'pytest', '--cov=.', '--cov-report=json', '--cov-report=term'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Try to read coverage.json if it exists
            if os.path.exists('coverage.json'):
                import json
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
                    return {
                        "success": True,
                        "percentage": coverage_data.get('totals', {}).get('percent_covered', 0),
                        "lines_covered": coverage_data.get('totals', {}).get('covered_lines', 0),
                        "lines_total": coverage_data.get('totals', {}).get('num_statements', 0)
                    }
            
            return {"success": False, "message": "Coverage report not generated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def improve(self) -> Dict[str, Any]:
        """
        Apply test improvements.
        
        Returns:
            Results of improvement actions
        """
        improvements = {
            "actions_taken": [],
            "errors": []
        }
        
        # Ensure tests directory exists
        if not os.path.exists(self.target_dir):
            try:
                os.makedirs(self.target_dir, exist_ok=True)
                improvements["actions_taken"].append({
                    "action": "create_tests_dir",
                    "status": f"Created tests directory at {self.target_dir}"
                })
            except Exception as e:
                improvements["errors"].append({
                    "action": "create_tests_dir",
                    "error": str(e)
                })
        
        # Create test subdirectories for organization
        test_subdirs = ['unit', 'integration', 'e2e']
        for subdir in test_subdirs:
            subdir_path = os.path.join(self.target_dir, subdir)
            if not os.path.exists(subdir_path):
                try:
                    os.makedirs(subdir_path, exist_ok=True)
                    # Create __init__.py
                    init_file = os.path.join(subdir_path, '__init__.py')
                    with open(init_file, 'w') as f:
                        f.write(f'"""Test {subdir} module."""\n')
                    
                    improvements["actions_taken"].append({
                        "action": "create_test_structure",
                        "status": f"Created {subdir} test directory"
                    })
                except Exception as e:
                    improvements["errors"].append({
                        "action": "create_test_structure",
                        "error": str(e)
                    })
        
        # Check for pytest.ini or setup.cfg
        has_pytest_config = os.path.exists('pytest.ini') or os.path.exists('setup.cfg')
        if not has_pytest_config:
            improvements["actions_taken"].append({
                "action": "config_check",
                "status": "Consider creating pytest.ini for test configuration"
            })
        
        return improvements
    
    def suggest_test_improvements(self) -> List[str]:
        """
        Generate test improvement suggestions.
        
        Returns:
            List of testing best practices
        """
        suggestions = [
            "Aim for 80%+ code coverage",
            "Write unit tests for all business logic functions",
            "Add integration tests for API endpoints",
            "Implement end-to-end tests for critical user flows",
            "Use fixtures and factories for test data",
            "Mock external dependencies in unit tests",
            "Add performance tests for critical operations",
            "Implement continuous testing in CI/CD pipeline",
            "Use parametrized tests to reduce code duplication",
            "Add tests for edge cases and error handling"
        ]
        return suggestions
