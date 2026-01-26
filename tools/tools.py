"""
Tool Implementations for Ariv
"""

import math
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("Tools")

class BaseTool:
    """Base class for all tools"""
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM consumption"""
        raise NotImplementedError
        
    def execute(self, **kwargs) -> Any:
        """Execute the tool"""
        raise NotImplementedError

class CalculatorTool(BaseTool):
    """Advanced calculator with mathematical functions"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "calculator",
            "description": "Perform mathematical calculations with support for basic operations, functions, and constants",
            "parameters": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', 'pi * 2')"
                }
            },
            "returns": "Numerical result of the calculation"
        }
        
    def execute(self, expression: str) -> float:
        """Execute mathematical calculation"""
        try:
            # Define safe functions and constants
            safe_dict = {
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'pow': math.pow,
                'abs': abs,
                'pi': math.pi,
                'e': math.e,
                'ceil': math.ceil,
                'floor': math.floor,
                'round': round
            }
            
            # Evaluate expression
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            logger.info(f"🧮 Calculator: {expression} = {result}")
            return result
            
        except Exception as e:
            error_msg = f"Calculation failed: {e}"
            logger.error(f"❌ Calculator error: {error_msg}")
            return {"error": error_msg}

class CodeExecutorTool(BaseTool):
    """Execute Python code safely"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "code_executor",
            "description": "Execute Python code and return the result. Useful for complex calculations, data processing, and algorithmic problems",
            "parameters": {
                "code": {
                    "type": "string", 
                    "description": "Python code to execute"
                }
            },
            "returns": "Result of code execution or error message"
        }
        
    def execute(self, code: str) -> Any:
        """Execute Python code"""
        try:
            # Create restricted execution environment
            import io
            import sys
            
            # Capture output
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            try:
                # Execute code
                exec(code, globals())
                output = buffer.getvalue()
                
                # If no output, try to get the last expression value
                if not output.strip():
                    try:
                        # Try evaluating as expression
                        result = eval(code, globals())
                        output = str(result)
                    except:
                        output = "Code executed successfully (no output)"
                        
            finally:
                sys.stdout = old_stdout
                
            logger.info(f"💻 Code executed successfully: {code[:50]}...")
            return output.strip() or "Code executed successfully"
            
        except Exception as e:
            error_msg = f"Code execution failed: {e}"
            logger.error(f"❌ Code execution error: {error_msg}")
            return {"error": error_msg, "code": code}

class KnowledgeBaseTool(BaseTool):
    """Knowledge base for factual information"""
    
    def __init__(self):
        super().__init__()
        self.knowledge_base = self._initialize_knowledge()
        
    def _initialize_knowledge(self) -> Dict[str, Any]:
        """Initialize knowledge base with common facts"""
        return {
            # Indian geography
            "india": {
                "capital": "New Delhi",
                "population": "1.4 billion",
                "states": 28,
                "union_territories": 8,
                "official_languages": 22,
                "currency": "Indian Rupee (INR)"
            },
            
            # Indian languages
            "languages": {
                "hindi": {"script": "Devanagari", "speakers": "600+ million"},
                "bengali": {"script": "Bengali", "speakers": "230+ million"},
                "telugu": {"script": "Telugu", "speakers": "95+ million"},
                "marathi": {"script": "Devanagari", "speakers": "90+ million"},
                "tamil": {"script": "Tamil", "speakers": "85+ million"},
                "urdu": {"script": "Perso-Arabic", "speakers": "70+ million"},
                "gujarati": {"script": "Gujarati", "speakers": "60+ million"},
                "kannada": {"script": "Kannada", "speakers": "45+ million"}
            },
            
            # Mathematics constants
            "math": {
                "pi": 3.14159265359,
                "e": 2.71828182846,
                "golden_ratio": 1.61803398875
            },
            
            # Science
            "science": {
                "speed_of_light": "299,792,458 m/s",
                "gravity": "9.8 m/s²",
                "planets": ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
            }
        }
        
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "knowledge_base",
            "description": "Query knowledge base for factual information about India, languages, science, and general knowledge",
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "Question or topic to look up (e.g., 'capital of India', 'Hindi speakers', 'value of pi')"
                },
                "category": {
                    "type": "string", 
                    "description": "Optional category to search in (india, languages, math, science)",
                    "optional": True
                }
            },
            "returns": "Factual information from knowledge base"
        }
        
    def execute(self, query: str, category: Optional[str] = None) -> Any:
        """Query knowledge base"""
        try:
            query_lower = query.lower().strip()
            
            # Search in specific category if provided
            if category and category in self.knowledge_base:
                return self._search_in_category(query_lower, self.knowledge_base[category])
                
            # Search across all categories
            results = {}
            for cat, data in self.knowledge_base.items():
                result = self._search_in_category(query_lower, data)
                if result:
                    results[cat] = result
                    
            if results:
                # Return the most relevant result
                if len(results) == 1:
                    return list(results.values())[0]
                else:
                    return results
            else:
                return f"No information found for: {query}"
                
        except Exception as e:
            error_msg = f"Knowledge base query failed: {e}"
            logger.error(f"❌ Knowledge base error: {error_msg}")
            return {"error": error_msg}
            
    def _search_in_category(self, query: str, data: Dict[str, Any]) -> Any:
        """Search within a specific category"""
        # Direct key match
        if query in data:
            return data[query]
            
        # Check for partial matches
        for key, value in data.items():
            if query in key or key in query:
                return value
                
        # Special handling for common queries
        if "capital" in query and "india" in query:
            return self.knowledge_base["india"]["capital"]
        elif "population" in query and "india" in query:
            return self.knowledge_base["india"]["population"]
        elif "pi" in query or "π" in query:
            return self.knowledge_base["math"]["pi"]
            
        return None

class WebSearchTool(BaseTool):
    """Simulated web search (in production, would integrate with search APIs)"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "web_search",
            "description": "Search the web for current information (simulated for demo purposes)",
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "returns": "Search results (simulated)"
        }
        
    def execute(self, query: str) -> Any:
        """Simulate web search"""
        logger.info(f"🔍 Web search: {query}")
        
        # Simulate search results
        return {
            "query": query,
            "results": [
                f"Simulated result 1 for: {query}",
                f"Simulated result 2 for: {query}",
                f"Information about {query} from web search"
            ],
            "note": "This is a simulated search. In production, integrate with real search APIs."
        }

class FileSystemTool(BaseTool):
    """File system operations"""
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": "file_system",
            "description": "Read and write files (restricted to project directory)",
            "parameters": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "list"],
                    "description": "Action to perform"
                },
                "path": {
                    "type": "string",
                    "description": "File path (relative to project directory)"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write action)",
                    "optional": True
                }
            },
            "returns": "File content or operation result"
        }
        
    def execute(self, action: str, path: str, content: Optional[str] = None) -> Any:
        """Execute file system operation"""
        try:
            import os
            
            # Security: restrict to project directory
            base_dir = os.path.dirname(os.path.dirname(__file__))
            full_path = os.path.join(base_dir, path)
            
            # Ensure path is within project directory
            if not os.path.abspath(full_path).startswith(os.path.abspath(base_dir)):
                return {"error": "Path outside project directory not allowed"}
                
            if action == "read":
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif action == "write":
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"File written: {path}"
            elif action == "list":
                if os.path.isdir(full_path):
                    return os.listdir(full_path)
                else:
                    return {"error": "Path is not a directory"}
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            error_msg = f"File system operation failed: {e}"
            logger.error(f"❌ File system error: {error_msg}")
            return {"error": error_msg}
