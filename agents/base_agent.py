"""Base agent class for all AI agents."""
import os
import json
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str, target_dir: str):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            target_dir: Directory that this agent is responsible for
        """
        self.name = name
        self.target_dir = target_dir
        self.log_file = f"logs/{name}_log.json"
        self.history: List[Dict[str, Any]] = []
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Ensure the log directory exists."""
        os.makedirs("logs", exist_ok=True)
    
    def log_action(self, action: str, details: Dict[str, Any], success: bool = True):
        """
        Log an action taken by the agent.
        
        Args:
            action: Description of the action
            details: Additional details about the action
            success: Whether the action was successful
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": self.name,
            "action": action,
            "details": details,
            "success": success
        }
        self.history.append(log_entry)
        
        # Append to log file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to write log: {e}")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent history of agent actions.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent log entries
        """
        return self.history[-limit:]
    
    def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze code quality and complexity.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Analysis results
        """
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic metrics
            lines = content.split('\n')
            loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Count functions and classes
            functions = len([line for line in lines if line.strip().startswith('def ')])
            classes = len([line for line in lines if line.strip().startswith('class ')])
            
            # Count comments and docstrings
            comments = len([line for line in lines if line.strip().startswith('#')])
            docstrings = content.count('"""') // 2 + content.count("'''") // 2
            
            return {
                "file": file_path,
                "lines_of_code": loc,
                "total_lines": len(lines),
                "functions": functions,
                "classes": classes,
                "comments": comments,
                "docstrings": docstrings,
                "comment_ratio": comments / max(loc, 1),
                "avg_function_length": loc / max(functions, 1) if functions > 0 else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run_linter(self, file_path: str) -> Dict[str, Any]:
        """
        Run linter on a file.
        
        Args:
            file_path: Path to the file to lint
            
        Returns:
            Linting results
        """
        try:
            # Try pylint first
            result = subprocess.run(
                ['python', '-m', 'pylint', file_path, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 or result.stdout:
                try:
                    return {"success": True, "issues": json.loads(result.stdout)}
                except json.JSONDecodeError:
                    return {"success": True, "issues": []}
            else:
                # Fallback to pycodestyle
                result = subprocess.run(
                    ['python', '-m', 'pycodestyle', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "success": True,
                    "issues": result.stdout.split('\n') if result.stdout else []
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_files_in_directory(self, extensions: List[str] = None) -> List[str]:
        """
        Get all files in the target directory.
        
        Args:
            extensions: List of file extensions to filter (e.g., ['.py', '.js'])
            
        Returns:
            List of file paths
        """
        if extensions is None:
            extensions = ['.py']
        
        files = []
        target_path = Path(self.target_dir)
        
        if not target_path.exists():
            return files
        
        for ext in extensions:
            files.extend(str(f) for f in target_path.rglob(f'*{ext}'))
        
        return files
    
    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the target directory/module.
        
        Returns:
            Analysis results with recommendations
        """
        pass
    
    @abstractmethod
    def improve(self) -> Dict[str, Any]:
        """
        Make improvements based on analysis.
        
        Returns:
            Results of improvement actions
        """
        pass
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent's analysis and improvement cycle.
        
        Returns:
            Combined results of analysis and improvements
        """
        print(f"[{self.name}] Starting analysis...")
        analysis = self.analyze()
        
        print(f"[{self.name}] Analysis complete. Starting improvements...")
        improvements = self.improve()
        
        result = {
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": analysis,
            "improvements": improvements
        }
        
        self.log_action("run_cycle", result)
        return result
