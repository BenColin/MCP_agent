#!/usr/bin/env python3
"""
LLM with MCP Tools Integration
集成MCP工具的LLM调用系统
"""

import asyncio
import json
import requests
from typing import Dict, List, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from tools.filesystem_tool import FileSystemTool
from tools.afm_tool import AFMTool
from tools.weather_tool import WeatherTool
from tools.file_tool import FileTool
from tools.time_tool import TimeTool
from tools.outfit_tool import OutfitTool

class LLMWithMCPTools:
    def __init__(self):
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.api_key = "YOUR_SILICONFLOW_API_KEY"
        self.model = "Pro/deepseek-ai/DeepSeek-V3.1-Terminus"
        self.mcp_session = None
        self.system_prompt = None
        
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
        
    async def initialize_mcp(self):
        """初始化MCP连接"""
        import os
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "mcp_tools_server.py")
        
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
        )
        
        self.stdio_client = stdio_client(server_params)
        self.read, self.write = await self.stdio_client.__aenter__()
        self.mcp_session = ClientSession(self.read, self.write)
        await self.mcp_session.__aenter__()
        await self.mcp_session.initialize()
        
    async def cleanup_mcp(self):
        """清理MCP连接"""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_client'):
            await self.stdio_client.__aexit__(None, None, None)
    
    def get_tools_definition(self) -> List[Dict]:
        """获取工具定义，用于LLM的tools参数；统一从工具模块生成"""
        def tool_to_llm_def(t) -> Dict:
            return {
                "type": "function",
                "function": {
                    "name": getattr(t, "name"),
                    "description": getattr(t, "description"),
                    "parameters": getattr(t, "inputSchema")
                }
            }

        tools: List[Dict] = []

        # 基础工具定义来自各自模块
        tools.append(tool_to_llm_def(WeatherTool.get_tool_definition()))
        tools.append(tool_to_llm_def(FileTool.get_tool_definition()))
        tools.append(tool_to_llm_def(TimeTool.get_tool_definition()))
        tools.append(tool_to_llm_def(OutfitTool.get_tool_definition()))

        # 文件系统工具（本身提供LLM函数式定义列表）
        filesystem_tool = FileSystemTool()
        tools.extend(filesystem_tool.get_tool_definition())

        # AFM 工具（本身提供LLM函数式定义列表）
        afm_tool = AFMTool()
        tools.extend(afm_tool.get_tool_definition())

        return tools
    
    

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """调用MCP工具"""
        try:
            result = await self.mcp_session.call_tool(tool_name, arguments)
            # 提取文本内容
            content_parts = []
            for content in result.content:
                if hasattr(content, 'text'):
                    content_parts.append(content.text)
            return "\n".join(content_parts)
        except Exception as e:
            return f"工具调用失败: {str(e)}"
    
    def call_llm(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """调用LLM API"""
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_data = response.json()
            
            # 检查API响应中的错误
            if response.status_code != 200:
                error_msg = response_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                raise Exception(f"API调用失败: {error_msg}")
            
            if 'error' in response_data:
                error_msg = response_data['error'].get('message', 'Unknown error')
                raise Exception(f"API返回错误: {error_msg}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析失败: {str(e)}")
        except Exception as e:
            if "Invalid request parameters" in str(e):
                raise Exception(f"API参数错误: {str(e)}")
            raise
    
    async def chat_with_tools(self, user_message: str, max_iterations: int = 5) -> str:
        """
        开始与LLM交互，支持工具调用，下述为系统默认提示词prompt
        """
        # 使用自定义系统提示或默认提示
        system_content = self.system_prompt if self.system_prompt else """你是一名多工具智能助手，需根据用户需求合理调用 MCP 工具完成任务。

工具使用准则：
1) 时间查询：当需要时间信息时，使用 `get_current_time` 获取当前系统时间（可带 `timezone` 和 `format`）。
2) 天气查询：当用户询问天气或搭配需要天气数据时，使用 `get_weather` 获取指定城市天气。
3) 穿衣建议：当用户需要穿衣/搭配方案时，调用 `generate_outfit_plan`，传入 `time`、`location`、`weather`、`temperature`。如信息不完整，先用相关工具补齐后再生成。
4) 保存内容：当用户要求保存或你认为有用时，调用 `save_outfit_plan`，`content` 为完整 Markdown 文档，`filename` 可选。
5) 文件操作：读写文件或目录浏览时，分别使用 `read_file`、`write_file`、`list_directory` 等文件系统工具。
6) AFM 辅助：涉及 AFM 寄存器/流程/故障检索，使用 `afm_*` 系列工具（寄存器列表、寄存器信息、值校验、模式标准流程、故障检索）。

回答策略：
- 在调用工具前先判断是否需要外部数据或副作用；只在必要时调用。
- 获取工具结果后，再综合生成清晰、结构化的回答。
- 对穿衣建议，确保包含：上身、下身、鞋履、配饰、外套、贴心提示与注意事项；充分考虑季节、温度、天气和时段；输出为完整 Markdown。
- 不要虚构工具或参数名；参数名须与工具定义一致。"""

        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        tools = self.get_tools_definition()
        
        for iteration in range(max_iterations):
            print(f"\n🔄 第 {iteration + 1} 轮对话...")
            
            # 调用LLM
            response = self.call_llm(messages, tools)
            
            if 'choices' not in response or not response['choices']:
                return "LLM调用失败，请检查API配置"
            
            assistant_message = response['choices'][0]['message']
            messages.append(assistant_message)
            
            # 检查是否有工具调用
            if assistant_message.get('tool_calls'):
                print(f"🔧 LLM请求调用工具...")
                
                for tool_call in assistant_message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    tool_args = json.loads(tool_call['function']['arguments'])
                    
                    print(f"   调用工具: {tool_name}")
                    print(f"   参数: {tool_args}")
                    
                    # 调用MCP工具
                    tool_result = await self.call_mcp_tool(tool_name, tool_args)
                    
                    # 将工具结果添加到消息历史
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": tool_result
                    })
                    
                    print(f"   工具结果: {tool_result[:100]}...")
                
                # 继续下一轮对话，让LLM处理工具结果
                continue
            else:
                # 没有工具调用，返回最终回答
                return assistant_message.get('content', '抱歉，我无法生成回答。')
        
        return "对话轮次超限，请重新开始。"

async def main():
    """主函数"""
    llm_system = LLMWithMCPTools()
    
    try:
        print("🚀 正在初始化MCP工具...")
        await llm_system.initialize_mcp()
        print("✅ MCP工具初始化完成!")
        
        print("\n🎯 进入交互式模式 (输入 'quit' 退出)")
        print("=" * 50)
        print("可用示例：天气查询、时间获取、文件操作、AFM助手、穿衣建议生成与保存")
        
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if user_input.lower() in ['quit', 'exit', '退出']:
                    break
                
                if not user_input:
                    continue
                
                response = await llm_system.chat_with_tools(user_input)
                print(f"🤖 助手: {response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
        
    except Exception as e:
        print(f"❌ 系统错误: {e}")
    finally:
        print("\n🔄 正在清理资源...")
        await llm_system.cleanup_mcp()
        print("👋 再见!")

if __name__ == "__main__":
    asyncio.run(main())