#!/usr/bin/env python3
"""
MCP服务器 - 重构版本
提供天气查询、时间获取和文件保存功能
使用模块化工具结构
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# 导入工具模块
from tools.weather_tool import WeatherTool
from tools.file_tool import FileTool
from tools.time_tool import TimeTool
from tools.outfit_tool import OutfitTool
from tools.filesystem_tool import FileSystemTool
from tools.afm_tool import AFMTool

# 创建MCP服务器实例
server = Server("weather-tool-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    列出可用的工具
    """
    filesystem_tool = FileSystemTool()
    afm_tool = AFMTool()
    tools = [
        WeatherTool.get_tool_definition(),
        FileTool.get_tool_definition(),
        TimeTool.get_tool_definition(),
        OutfitTool.get_tool_definition()
    ]
    
    # 添加文件系统工具定义
    for tool_def in filesystem_tool.get_tool_definition():
        tools.append(Tool(
            name=tool_def["function"]["name"],
            description=tool_def["function"]["description"],
            inputSchema=tool_def["function"]["parameters"]
        ))
    # 添加 AFM 工具定义
    for tool_def in afm_tool.get_tool_definition():
        tools.append(Tool(
            name=tool_def["function"]["name"],
            description=tool_def["function"]["description"],
            inputSchema=tool_def["function"]["parameters"]
        ))
    
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    处理工具调用
    """
    if name == "get_weather":
        return WeatherTool.handle_get_weather(arguments)
    elif name == "save_outfit_plan":
        return FileTool.handle_save_outfit_plan(arguments)
    elif name == "get_current_time":
        return TimeTool.handle_get_current_time(arguments)
    elif name == "generate_outfit_plan":
        return OutfitTool.handle_generate_outfit_plan(arguments)
    # 文件系统工具
    elif name in ["read_file", "write_file", "list_directory", "create_directory", 
                  "search_files", "get_file_info", "move_file", "edit_file"]:
        filesystem_tool = FileSystemTool()
        
        # 调用对应的文件系统工具方法
        if name == "read_file":
            result = filesystem_tool.read_file(arguments.get("path", ""))
        elif name == "write_file":
            result = filesystem_tool.write_file(
                arguments.get("path", ""), 
                arguments.get("content", "")
            )
        elif name == "list_directory":
            result = filesystem_tool.list_directory(arguments.get("path", ""))
        elif name == "create_directory":
            result = filesystem_tool.create_directory(arguments.get("path", ""))
        elif name == "search_files":
            result = filesystem_tool.search_files(
                arguments.get("path", ""),
                arguments.get("pattern", ""),
                arguments.get("exclude_patterns", [])
            )
        elif name == "get_file_info":
            result = filesystem_tool.get_file_info(arguments.get("path", ""))
        elif name == "move_file":
            result = filesystem_tool.move_file(
                arguments.get("source", ""),
                arguments.get("destination", "")
            )
        elif name == "edit_file":
            result = filesystem_tool.edit_file(
                arguments.get("path", ""),
                arguments.get("old_text", ""),
                arguments.get("new_text", ""),
                arguments.get("dry_run", False)
            )
        
        return [TextContent(type="text", text=result)]
    # AFM 工具
    elif name in [
        "afm_list_registers",
        "afm_get_register_info",
        "afm_validate_register_value",
        "afm_get_mode_standard_flow",
        "afm_search_troubleshooting"
    ]:
        afm_tool = AFMTool()
        if name == "afm_list_registers":
            return afm_tool.handle_afm_list_registers(arguments)
        elif name == "afm_get_register_info":
            return afm_tool.handle_afm_get_register_info(arguments)
        elif name == "afm_validate_register_value":
            return afm_tool.handle_afm_validate_register_value(arguments)
        elif name == "afm_get_mode_standard_flow":
            return afm_tool.handle_afm_get_mode_standard_flow(arguments)
        elif name == "afm_search_troubleshooting":
            return afm_tool.handle_afm_search_troubleshooting(arguments)
    else:
        raise ValueError(f"未知工具: {name}")

# 工具处理函数已移至独立的工具模块中

async def main():
    """
    启动MCP服务器
    """
    # 使用stdio传输协议运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())