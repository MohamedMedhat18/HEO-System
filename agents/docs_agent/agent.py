"""Documentation Agent for analyzing and improving project documentation."""
import os
from typing import Dict, Any, List
from pathlib import Path
from agents.base_agent import BaseAgent


class DocsAgent(BaseAgent):
    """Agent responsible for documentation improvements."""
    
    def __init__(self):
        """Initialize the Documentation Agent."""
        super().__init__(name="docs_agent", target_dir=".")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze project documentation.
        
        Returns:
            Analysis results with documentation recommendations
        """
        analysis_results = {
            "files_found": [],
            "missing_docs": [],
            "recommendations": []
        }
        
        # Check for essential documentation files
        essential_docs = {
            "README.md": "Project overview and setup instructions",
            "CONTRIBUTING.md": "Contribution guidelines",
            "LICENSE": "License information",
            "CHANGELOG.md": "Version history and changes",
            "docs/API.md": "API documentation",
            "docs/ARCHITECTURE.md": "System architecture documentation",
            "docs/DEPLOYMENT.md": "Deployment guide"
        }
        
        for doc_file, description in essential_docs.items():
            file_path = os.path.join(self.target_dir, doc_file)
            if os.path.exists(file_path):
                analysis_results["files_found"].append({
                    "file": doc_file,
                    "status": "exists",
                    "description": description
                })
            else:
                analysis_results["missing_docs"].append({
                    "file": doc_file,
                    "description": description,
                    "priority": "high" if doc_file in ["README.md", "LICENSE"] else "medium"
                })
        
        # Analyze README.md if it exists
        readme_path = os.path.join(self.target_dir, "README.md")
        if os.path.exists(readme_path):
            readme_analysis = self._analyze_readme(readme_path)
            analysis_results["readme_analysis"] = readme_analysis
        
        # Check for inline documentation in Python files
        py_files = self._get_python_files()
        documented_files = 0
        total_functions = 0
        documented_functions = 0
        
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Count docstrings
                    if '"""' in content or "'''" in content:
                        documented_files += 1
                    
                    # Count functions and their docstrings
                    lines = content.split('\n')
                    in_function = False
                    for i, line in enumerate(lines):
                        if line.strip().startswith('def '):
                            total_functions += 1
                            # Check if next non-empty line is a docstring
                            for j in range(i + 1, min(i + 5, len(lines))):
                                if lines[j].strip():
                                    if '"""' in lines[j] or "'''" in lines[j]:
                                        documented_functions += 1
                                    break
            except Exception:
                pass
        
        doc_coverage = (documented_functions / max(total_functions, 1)) * 100
        
        analysis_results["code_documentation"] = {
            "total_files": len(py_files),
            "documented_files": documented_files,
            "total_functions": total_functions,
            "documented_functions": documented_functions,
            "coverage_percentage": round(doc_coverage, 2)
        }
        
        # Recommendations
        if doc_coverage < 80:
            analysis_results["recommendations"].append({
                "type": "code_documentation",
                "message": f"Documentation coverage is {doc_coverage:.1f}%. Aim for 80%+ coverage.",
                "priority": "high"
            })
        
        if len(analysis_results["missing_docs"]) > 0:
            analysis_results["recommendations"].append({
                "type": "project_docs",
                "message": f"Missing {len(analysis_results['missing_docs'])} essential documentation files",
                "priority": "high"
            })
        
        return analysis_results
    
    def _analyze_readme(self, readme_path: str) -> Dict[str, Any]:
        """Analyze README.md content."""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for essential sections
            essential_sections = [
                "installation", "usage", "features", "requirements",
                "setup", "configuration", "api", "examples"
            ]
            
            found_sections = []
            for section in essential_sections:
                if section.lower() in content.lower():
                    found_sections.append(section)
            
            return {
                "length": len(content),
                "has_code_blocks": "```" in content,
                "has_images": "![" in content or "<img" in content,
                "has_links": "[" in content and "](" in content,
                "sections_found": found_sections,
                "completeness": len(found_sections) / len(essential_sections) * 100
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_python_files(self) -> List[str]:
        """Get all Python files in the project."""
        python_files = []
        for root, dirs, files in os.walk(self.target_dir):
            # Skip venv and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv']
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def improve(self) -> Dict[str, Any]:
        """
        Apply documentation improvements.
        
        Returns:
            Results of improvement actions
        """
        improvements = {
            "actions_taken": [],
            "errors": []
        }
        
        # Create docs directory if it doesn't exist
        docs_dir = os.path.join(self.target_dir, "docs")
        if not os.path.exists(docs_dir):
            try:
                os.makedirs(docs_dir, exist_ok=True)
                improvements["actions_taken"].append({
                    "action": "create_docs_dir",
                    "status": f"Created docs directory at {docs_dir}"
                })
            except Exception as e:
                improvements["errors"].append({
                    "action": "create_docs_dir",
                    "error": str(e)
                })
        
        # Check if README has basic structure
        readme_path = os.path.join(self.target_dir, "README.md")
        if os.path.exists(readme_path):
            improvements["actions_taken"].append({
                "action": "readme_check",
                "status": "README.md exists"
            })
        else:
            improvements["actions_taken"].append({
                "action": "readme_check",
                "status": "README.md needs to be created"
            })
        
        return improvements
    
    def generate_api_docs(self) -> str:
        """
        Generate API documentation from FastAPI app.
        
        Returns:
            Generated API documentation as markdown
        """
        docs = "# API Documentation\n\n"
        docs += "## Overview\n\n"
        docs += "This document describes the REST API endpoints available in the HEO System.\n\n"
        
        # This would ideally parse the FastAPI app and generate docs
        # For now, we'll provide a template
        docs += "## Authentication\n\n"
        docs += "### POST /api/auth/login\n"
        docs += "Authenticate a user.\n\n"
        docs += "### POST /api/auth/register\n"
        docs += "Register a new user.\n\n"
        
        docs += "## Invoices\n\n"
        docs += "### GET /api/invoices\n"
        docs += "List all invoices.\n\n"
        docs += "### POST /api/invoices\n"
        docs += "Create a new invoice.\n\n"
        
        return docs
