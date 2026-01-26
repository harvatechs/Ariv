"""
Tool Registry - Dynamic tool management for Ariv
"""

import json
import ast
import logging
from typing import Dict, List, Any, Optional, Callable
from .tools import CalculatorTool, CodeExecutorTool, KnowledgeBaseTool

logger = logging.getLogger("ToolRegistry")

class ToolExecutionError(Exception):
    """Exception raised when tool execution fails"""
    pass

class ToolRegistry:
    """Registry for managing and executing tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_builtin_tools()
        
    def _register_builtin_tools(self):
        """Register built-in tools"""
        self.register("calculator", CalculatorTool())
        self.register("code_executor", CodeExecutorTool())
        self.register("knowledge_base", KnowledgeBaseTool())
        
    def register(self, name: str, tool: Any):
        """Register a tool"""
        if not hasattr(tool, 'execute'):
            raise ValueError(f"Tool {name} must have an execute method")
        if not hasattr(tool, 'get_schema'):
            raise ValueError(f"Tool {name} must have a get_schema method")
            
        self.tools[name] = tool
        logger.info(f"✅ Registered tool: {name}")
        
    def unregister(self, name: str):
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"🗑️  Unregistered tool: {name}")
            
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name"""
        return self.tools.get(name)
        
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
        
    def get_tool_info(self, tools: Optional[List[str]] = None) -> str:
        """Get formatted information about tools"""
        if tools is None:
            tools = self.get_available_tools()
            
        info_parts = []
        for tool_name in tools:
            tool = self.get_tool(tool_name)
            if tool:
                schema = tool.get_schema()
                info_parts.append(f"- {tool_name}: {schema.get('description', 'No description')}")
                
        return "\n".join(info_parts) if info_parts else "No tools available"
        
    def execute_tool_call(self, tool_call_str: str) -> Any:
        """
        Execute a tool call from string
        
        Expected format: tool_name(arg1=value1, arg2=value2)
        """
        try:
            # Parse tool call
            tool_call_str = tool_call_str.strip()
            
            # Extract tool name and arguments
            if '(' not in tool_call_str or ')' not in tool_call_str:
                raise ValueError("Invalid tool call format")
                
            tool_name = tool_call_str.split('(')[0].strip()
            args_str = tool_call_str[len(tool_name)+1:-1].strip()
            
            # Get tool
            tool = self.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            # Parse arguments
            if args_str:
                # Try to parse as keyword arguments
                try:
                    # Create a safe dict for eval
                    safe_dict = {"__builtins__": {}}
                    args = eval(f"dict({args_str})", safe_dict)
                except:
                    # If that fails, treat as positional
                    args = {"input": args_str}
            else:
                args = {}
                
            # Execute tool
            logger.info(f"🔧 Executing tool: {tool_name} with args: {args}")
            result = tool.execute(**args)
            logger.info(f"✅ Tool {tool_name} executed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Tool execution failed: {e}"
            logger.error(f"❌ {error_msg}")
            raise ToolExecutionError(error_msg)
            
    def execute(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool directly"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")
            
        return tool.execute(**kwargs)
