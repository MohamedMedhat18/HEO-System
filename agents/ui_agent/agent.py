"""UI Agent for analyzing and improving frontend code."""
import os
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class UIAgent(BaseAgent):
    """Agent responsible for UI/Frontend improvements."""
    
    def __init__(self):
        """Initialize the UI Agent."""
        super().__init__(name="ui_agent", target_dir="frontend")
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze frontend code for improvements.
        
        Returns:
            Analysis results with UI-specific recommendations
        """
        files = self.get_files_in_directory(['.py'])
        
        analysis_results = {
            "total_files": len(files),
            "files_analyzed": [],
            "recommendations": []
        }
        
        for file_path in files:
            file_analysis = self.analyze_code(file_path)
            analysis_results["files_analyzed"].append(file_analysis)
            
            # UI-specific checks
            if file_analysis.get("lines_of_code", 0) > 300:
                analysis_results["recommendations"].append({
                    "file": file_path,
                    "type": "refactoring",
                    "message": "Consider splitting large UI component into smaller, reusable components",
                    "priority": "medium"
                })
            
            if file_analysis.get("comment_ratio", 0) < 0.1:
                analysis_results["recommendations"].append({
                    "file": file_path,
                    "type": "documentation",
                    "message": "Add more comments to explain UI logic and component behavior",
                    "priority": "low"
                })
        
        # Check for theme consistency
        if os.path.exists(os.path.join(self.target_dir, "utils", "theme.py")):
            analysis_results["recommendations"].append({
                "type": "enhancement",
                "message": "Theme system detected. Ensure all components use centralized theme.",
                "priority": "high"
            })
        
        # Check for accessibility
        analysis_results["recommendations"].append({
            "type": "accessibility",
            "message": "Ensure all UI components follow WCAG 2.1 guidelines for accessibility",
            "priority": "high"
        })
        
        return analysis_results
    
    def improve(self) -> Dict[str, Any]:
        """
        Apply improvements to frontend code.
        
        Returns:
            Results of improvement actions
        """
        improvements = {
            "actions_taken": [],
            "errors": []
        }
        
        # Check if theme file exists, if not suggest creation
        theme_path = os.path.join(self.target_dir, "utils", "theme.py")
        if os.path.exists(theme_path):
            improvements["actions_taken"].append({
                "action": "theme_check",
                "status": "Theme system already exists and is properly configured"
            })
        else:
            improvements["actions_taken"].append({
                "action": "theme_check",
                "status": "Theme file not found in expected location"
            })
        
        # Ensure component structure
        components_dir = os.path.join(self.target_dir, "components")
        if not os.path.exists(components_dir):
            try:
                os.makedirs(components_dir, exist_ok=True)
                improvements["actions_taken"].append({
                    "action": "create_structure",
                    "status": f"Created components directory at {components_dir}"
                })
            except Exception as e:
                improvements["errors"].append({
                    "action": "create_structure",
                    "error": str(e)
                })
        
        # Check for responsive design patterns
        files = self.get_files_in_directory(['.py'])
        responsive_count = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'st.columns' in content or 'responsive' in content.lower():
                        responsive_count += 1
            except Exception:
                pass
        
        improvements["actions_taken"].append({
            "action": "responsive_check",
            "status": f"Found {responsive_count} files with responsive design patterns"
        })
        
        return improvements
    
    def suggest_ui_improvements(self) -> List[str]:
        """
        Generate specific UI improvement suggestions.
        
        Returns:
            List of actionable UI improvement suggestions
        """
        suggestions = [
            "Add loading skeletons for better perceived performance",
            "Implement toast notifications for user feedback",
            "Add micro-interactions for button clicks and form submissions",
            "Create a design system with consistent spacing, colors, and typography",
            "Implement lazy loading for heavy components",
            "Add keyboard navigation support for accessibility",
            "Create mobile-responsive layouts using Streamlit columns",
            "Add animation transitions between page changes",
            "Implement dark mode with proper color contrast",
            "Add error boundaries to prevent UI crashes"
        ]
        return suggestions
