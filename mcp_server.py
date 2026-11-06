#!/usr/bin/env python3
"""
MCP服务器 - 重构版本
提供天气查询、时间获取和文件保存功能
使用模块化工具结构
"""

import asyncio
import sys
import os
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# 导入工具模块
from tools.weather_tool import WeatherTool
from tools.file_tool import FileTool
from tools.time_tool import TimeTool
from tools.filesystem_tool import FileSystemTool
from tools.afm_tool import AFMTool
from tools.afm_semantic_tool import AFMSemanticTool
from tools.outfit_tool import OutfitTool

# 创建MCP服务器实例
server = Server("mcp-tool-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出可用的工具"""
    tools = [WeatherTool.get_tool_definition(), FileTool.get_tool_definition(), 
             TimeTool.get_tool_definition(), OutfitTool.get_tool_definition()]
    
    for tool_def in FileSystemTool().get_tool_definition():
        tools.append(Tool(name=tool_def["function"]["name"], description=tool_def["function"]["description"], 
                         inputSchema=tool_def["function"]["parameters"]))
    for tool_def in AFMTool().get_tool_definition():
        tools.append(Tool(name=tool_def["function"]["name"], description=tool_def["function"]["description"], 
                         inputSchema=tool_def["function"]["parameters"]))
    for tool_def in AFMSemanticTool().get_tool_definition():
        tools.append(Tool(name=tool_def["function"]["name"], description=tool_def["function"]["description"], 
                         inputSchema=tool_def["function"]["parameters"]))
    
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    if name == "get_weather":
        return WeatherTool.handle_get_weather(arguments)
    elif name == "save_outfit_plan":
        return FileTool.handle_save_outfit_plan(arguments)
    elif name == "get_current_time":
        return TimeTool.handle_get_current_time(arguments)
    elif name == "generate_outfit_plan":
        return OutfitTool.handle_generate_outfit_plan(arguments)
    elif name in ["read_file", "write_file", "list_directory", "create_directory", 
                  "search_files", "get_file_info", "move_file", "edit_file"]:
        filesystem_tool = FileSystemTool()
        method_map = {"read_file": filesystem_tool.read_file, "write_file": filesystem_tool.write_file,
                      "list_directory": filesystem_tool.list_directory, "create_directory": filesystem_tool.create_directory,
                      "search_files": filesystem_tool.search_files, "get_file_info": filesystem_tool.get_file_info,
                      "move_file": filesystem_tool.move_file, "edit_file": filesystem_tool.edit_file}
        if name == "write_file":
            result = method_map[name](arguments.get("path", ""), arguments.get("content", ""))
        elif name == "search_files":
            result = method_map[name](arguments.get("path", ""), arguments.get("pattern", ""), arguments.get("exclude_patterns", []))
        elif name == "move_file":
            result = method_map[name](arguments.get("source", ""), arguments.get("destination", ""))
        elif name == "edit_file":
            result = method_map[name](arguments.get("path", ""), arguments.get("old_text", ""), 
                                     arguments.get("new_text", ""), arguments.get("dry_run", False))
        else:
            result = method_map[name](arguments.get("path", ""))
        return [TextContent(type="text", text=result)]
    elif name in ["get_afm_prompt", "query_afm_issue", "validate_afm_registers", "search_protocol_register", "search_afm_issue_semantic"]:
        if name == "search_afm_issue_semantic":
            sem_tool = AFMSemanticTool()
            return [TextContent(type="text", text=json.dumps(sem_tool.handle_search_afm_issue_semantic(
                query=arguments.get("query", ""), category=arguments.get("category"),
                top_k=int(arguments.get("top_k", 3) or 3), use=arguments.get("use", "rerank"),
                model=arguments.get("model"), api_key=arguments.get("api_key")), ensure_ascii=False))]
        else:
            afm_tool = AFMTool()
            method_map = {"get_afm_prompt": afm_tool.handle_get_afm_prompt, "query_afm_issue": afm_tool.handle_query_afm_issue,
                          "validate_afm_registers": afm_tool.handle_validate_afm_registers, 
                          "search_protocol_register": afm_tool.handle_search_protocol_register}
            return method_map[name](arguments)
    
    raise ValueError(f"未知工具: {name}")

# 工具处理函数已移至独立的工具模块中

async def main():
    """启动MCP服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())