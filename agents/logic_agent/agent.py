"""Logic Agent for analyzing and improving backend code."""
import os
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class LogicAgent(BaseAgent):
    """Agent responsible for backend logic improvements."""
    
    def __init__(self):
        """Initialize the Logic Agent."""
        super().__init__(name="logic_agent", target_dir="backend")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze backend code for improvements.
        
        Returns:
            Analysis results with backend-specific recommendations
        """
        files = self.get_files_in_directory(['.py'])
        
        analysis_results = {
            "total_files": len(files),
            "files_analyzed": [],
            "recommendations": [],
            "security_checks": []
        }
        
        for file_path in files:
            file_analysis = self.analyze_code(file_path)
            analysis_results["files_analyzed"].append(file_analysis)
            
            # Backend-specific checks
            if file_analysis.get("lines_of_code", 0) > 500:
                analysis_results["recommendations"].append({
                    "file": file_path,
                    "type": "refactoring",
                    "message": "Consider breaking down large service files into smaller modules",
                    "priority": "high"
                })
            
            if file_analysis.get("docstrings", 0) < file_analysis.get("functions", 1):
                analysis_results["recommendations"].append({
                    "file": file_path,
                    "type": "documentation",
                    "message": "Add docstrings to all functions for better API documentation",
                    "priority": "medium"
                })
            
            # Security checks
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for potential security issues
                    if 'password' in content.lower() and 'hash' not in content.lower():
                        analysis_results["security_checks"].append({
                            "file": file_path,
                            "issue": "Potential insecure password handling",
                            "severity": "high"
                        })
                    
                    if 'sql' in content.lower() and 'execute(' in content:
                        if '?' not in content and '%s' not in content:
                            analysis_results["security_checks"].append({
                                "file": file_path,
                                "issue": "Potential SQL injection vulnerability",
                                "severity": "critical"
                            })
                    
                    if 'os.system' in content or 'subprocess.call' in content:
                        analysis_results["security_checks"].append({
                            "file": file_path,
                            "issue": "System command execution detected - ensure input validation",
                            "severity": "high"
                        })
            except Exception:
                pass
        
        # Check for proper error handling
        analysis_results["recommendations"].append({
            "type": "error_handling",
            "message": "Ensure all API endpoints have proper try-except blocks",
            "priority": "high"
        })
        
        # Check for API documentation
        if os.path.exists(os.path.join(self.target_dir, "api", "main.py")):
            analysis_results["recommendations"].append({
                "type": "documentation",
                "message": "Ensure FastAPI endpoints have proper docstrings and response models",
                "priority": "medium"
            })
        
        return analysis_results
    
    def improve(self) -> Dict[str, Any]:
        """
        Apply improvements to backend code.
        
        Returns:
            Results of improvement actions
        """
        improvements = {
            "actions_taken": [],
            "errors": []
        }
        
        # Check database migrations
        migrations_dir = os.path.join(self.target_dir, "migrations")
        if not os.path.exists(migrations_dir):
            try:
                os.makedirs(migrations_dir, exist_ok=True)
                improvements["actions_taken"].append({
                    "action": "create_migrations_dir",
                    "status": f"Created migrations directory at {migrations_dir}"
                })
            except Exception as e:
                improvements["errors"].append({
                    "action": "create_migrations_dir",
                    "error": str(e)
                })
        
        # Check for proper service layer
        services_dir = os.path.join(self.target_dir, "services")
        if os.path.exists(services_dir):
            improvements["actions_taken"].append({
                "action": "architecture_check",
                "status": "Service layer properly structured"
            })
        else:
            improvements["actions_taken"].append({
                "action": "architecture_check",
                "status": "Consider implementing service layer pattern"
            })
        
        # Check for API versioning
        api_dir = os.path.join(self.target_dir, "api")
        if os.path.exists(api_dir):
            files = os.listdir(api_dir)
            if any('v1' in f or 'v2' in f for f in files):
                improvements["actions_taken"].append({
                    "action": "versioning_check",
                    "status": "API versioning implemented"
                })
            else:
                improvements["actions_taken"].append({
                    "action": "versioning_check",
                    "status": "Consider implementing API versioning for future compatibility"
                })
        
        # Check for validation
        files = self.get_files_in_directory(['.py'])
        pydantic_count = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'pydantic' in content.lower() or 'BaseModel' in content:
                        pydantic_count += 1
            except Exception:
                pass
        
        improvements["actions_taken"].append({
            "action": "validation_check",
            "status": f"Found {pydantic_count} files using Pydantic for data validation"
        })
        
        return improvements
    
    def suggest_performance_improvements(self) -> List[str]:
        """
        Generate performance improvement suggestions.
        
        Returns:
            List of performance optimization suggestions
        """
        suggestions = [
            "Implement database connection pooling",
            "Add caching layer (Redis) for frequently accessed data",
            "Use database indexes on frequently queried columns",
            "Implement pagination for large data sets",
            "Add async/await for I/O operations",
            "Implement request rate limiting",
            "Use bulk operations for database writes",
            "Add database query optimization",
            "Implement background task queue for long-running operations",
            "Add monitoring and logging for performance metrics"
        ]
        return suggestions
