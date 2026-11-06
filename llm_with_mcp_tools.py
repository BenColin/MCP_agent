#!/usr/bin/env python3
"""
LLM with MCP Tools Integration
集成MCP工具的LLM调用系统 + 上下文工程
"""

import asyncio
import sys
import json
import requests
from typing import Dict, List, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from tools.filesystem_tool import FileSystemTool
from tools.afm_tool import AFMTool
from tools.afm_semantic_tool import AFMSemanticTool
from tools.weather_tool import WeatherTool
from tools.time_tool import TimeTool
from tools.file_tool import FileTool
from tools.outfit_tool import OutfitTool
from context_manager import create_context_system, MemoryManager, ShortTermMemory, ContextEngineer

class LLMWithMCPTools:
    def __init__(self, enable_context_engineering: bool = True, memory_dir: str = "memory"):
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.api_key = "YOUR_SILICONFLOW_API_KEY"
        self.model = "Pro/deepseek-ai/DeepSeek-V3.1-Terminus"
        self.mcp_session: Optional[ClientSession] = None
        self.system_prompt: Optional[str] = None
        
        # 上下文工程组件
        self.enable_context_engineering = enable_context_engineering
        if enable_context_engineering:
            self.memory_manager, self.short_term_memory, self.context_engineer = create_context_system(memory_dir)
            print(f"✅ 上下文工程已启用（记忆目录: {memory_dir}）")
        else:
            self.memory_manager = None
            self.short_term_memory = None
            self.context_engineer = None
        
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
        
    async def initialize_mcp(self):
        """初始化MCP连接"""
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_params = StdioServerParameters(command=sys.executable, args=[os.path.join(current_dir, "mcp_server.py")])
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
        """获取工具定义，用于LLM的tools参数"""
        tools = [WeatherTool.get_llm_tool_definition(), FileTool.get_llm_tool_definition(), 
                 TimeTool.get_llm_tool_definition(), OutfitTool.get_llm_tool_definition()]
        tools.extend(FileSystemTool().get_tool_definition())
        tools.extend(AFMTool().get_tool_definition())
        tools.extend(AFMSemanticTool().get_tool_definition())
        return tools
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """调用MCP工具"""
        try:
            if self.mcp_session is None:
                return "工具调用失败: MCP会话未初始化"
            result = await self.mcp_session.call_tool(tool_name, arguments)
            return "\n".join([c.text for c in result.content if hasattr(c, 'text') and c.type == 'text'])
        except Exception as e:
            return f"工具调用失败: {str(e)}"
    
    def call_llm(self, messages: List[Dict], tools: Optional[List[Dict]] = None) -> Dict:
        """调用LLM API"""
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response_data = response.json()
            
            if response.status_code != 200 or 'error' in response_data:
                error_msg = response_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                raise Exception(f"API调用失败: {error_msg}")
            
            return response_data
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise Exception(f"请求失败: {str(e)}")
    
    async def chat_with_tools(self, user_message: str, max_iterations: int = 15, save_to_memory: bool = True) -> str:
        """
        与LLM对话，支持工具调用 + 上下文工程
        
        Args:
            user_message: 用户输入
            max_iterations: 最大对话轮次
            save_to_memory: 是否将对话保存到记忆中
        """
        # 使用自定义系统提示或默认提示
        base_system_prompt = self.system_prompt if self.system_prompt else """你是一个多工具智能助手，需根据用户需求自动选择并调用合适的工具完成任务。

工具使用原则：
1. 时间查询：当需要时间信息时，使用 get_current_time 获取当前系统时间。
2. 天气查询：当用户询问天气时，使用 get_weather 获取准确的天气信息。
3. 穿衣建议：当用户需要穿衣方案时，先调用 generate_outfit_plan 生成markdown内容；如用户要求保存文件，再调用 save_outfit_plan 将内容保存为 .md 文件。
4. 文件系统：涉及读写/编辑/移动/目录等操作时，优先使用文件系统工具（read_file, write_file, list_directory, create_directory, search_files, get_file_info, move_file, edit_file）。
5. AFM领域：
   - 当用户提出自然语言问题或模糊检索时，调用 search_afm_issue_semantic（支持 rerank/embedding，优先 rerank）。
   - 当用户提供明确的分类/编号时，调用 query_afm_issue。
   - 当用户需要查找寄存器/协议字段时，调用 search_protocol_register。
   - 当用户需要校验寄存器配置是否符合规范时，调用 validate_afm_registers。

对话原则：
- 记住用户的偏好和重要信息，在后续对话中体现连贯性。
- 不要臆断；当信息不足时请提问澄清或说明假设。
- 输出简洁、结构化，优先返回可执行结果或清晰的markdown内容。
- 尽量避免冗长的解释，专注于高质量结果与准确工具调用。"""

        # 构建消息列表（使用上下文工程或传统方式）
        if self.enable_context_engineering and self.short_term_memory and self.context_engineer:
            # 添加用户消息到短期记忆
            self.short_term_memory.add_message("user", user_message)
            
            # 动态构建包含上下文的消息
            messages = self.context_engineer.build_messages_with_context(
                system_prompt=base_system_prompt,
                include_knowledge=False,  # 可根据需要开启
                knowledge_query=user_message if len(user_message) > 10 else None
            )
        else:
            messages = [
                {
                    "role": "system",
                    "content": base_system_prompt
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
                    
                    messages.append({"role": "tool", "tool_call_id": tool_call['id'], "content": tool_result})
                    print(f"   工具结果: {tool_result[:100]}...")
                
                # 继续下一轮对话，让LLM处理工具结果
                continue
            else:
                # 没有工具调用，返回最终回答
                final_response = assistant_message.get('content', '抱歉，我无法生成回答。')
                
                # 保存助手回复到短期记忆
                if self.enable_context_engineering and self.short_term_memory and self.context_engineer:
                    self.short_term_memory.add_message("assistant", final_response)
                    
                    # 判断是否需要保存到长期记忆
                    if save_to_memory:
                        save_decision = self.context_engineer.should_save_to_long_term(
                            user_message, final_response
                        )
                        if save_decision["should_save"]:
                            print(f"💾 检测到重要信息，已保存到长期记忆（类型: {save_decision['save_type']}）")
                            self.context_engineer.process_save_decision(save_decision)
                
                return final_response
        
        return "对话轮次超限，请重新开始。"
    
    def clear_session(self, save_summary: bool = True):
        """清除当前会话并可选保存会话摘要"""
        if self.enable_context_engineering and save_summary and self.short_term_memory and self.memory_manager:
            self.memory_manager.save_session(self.short_term_memory.get_conversation_summary())
            self.short_term_memory.clear()
            print("✅ 会话已保存到长期记忆\n🔄 短期记忆已清空")
    
    def get_memory_status(self) -> Dict[str, Any]:
        """获取记忆系统状态"""
        if not self.enable_context_engineering or not self.memory_manager or not self.short_term_memory:
            return {"context_engineering": "disabled"}
        
        return {
            "context_engineering": "enabled",
            "short_term_messages": len(self.short_term_memory.get_messages()),
            "user_profile": {
                "name": self.memory_manager.user_profile.get("name"),
                "preferences_count": len(self.memory_manager.user_profile.get("preferences", {})),
                "important_facts_count": len(self.memory_manager.user_profile.get("important_facts", []))
            },
            "session_history_count": len(self.memory_manager.session_history.get("sessions", [])),
            "knowledge_base_facts": len(self.memory_manager.knowledge_base.get("facts", []))
        }

async def main():
    """主函数 - 支持上下文工程的交互式对话"""
    llm_system = LLMWithMCPTools(enable_context_engineering=True)
    
    try:
        print("🚀 正在初始化MCP工具...")
        await llm_system.initialize_mcp()
        print("✅ MCP工具初始化完成!")
        
        print("\n🤖 LLM + MCP + 上下文工程 智能助手已启动")
        print("=" * 50)
        print("🎯 进入交互式模式 (输入 'quit' 退出)")
        print("提示：可询问天气、生成穿衣建议、进行AFM问题检索/协议搜索/寄存器校验，或执行文件系统操作。")
        print("\n💡 特殊命令:")
        print("  - 'clear' / '清除': 清除当前会话记忆")
        print("  - 'status' / '状态': 查看记忆系统状态")
        print("  - 'help' / '帮助': 查看可用功能")
        
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if user_input.lower() in ['quit', 'exit', '退出']:
                    # 保存会话摘要
                    llm_system.clear_session(save_summary=True)
                    break
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if user_input.lower() in ['clear', '清除']:
                    llm_system.clear_session(save_summary=True)
                    print("✅ 会话已清除，可以开始新对话了！")
                    continue
                elif user_input.lower() in ['status', '状态']:
                    print("\n📊 记忆系统状态:", json.dumps(llm_system.get_memory_status(), ensure_ascii=False, indent=2))
                    continue
                elif user_input.lower() in ['help', '帮助']:
                    print("\n🔧 可用功能:")
                    print("  - 天气查询: 询问任何城市的天气情况")
                    print("  - 文件操作: 读写文件、创建目录等")
                    print("  - 时间查询: 获取当前时间")
                    print("  - 穿衣建议: 输入时间/地点/天气/温度生成markdown方案，可保存为md")
                    print("  - AFM工具: 语义检索常见问题、协议寄存器搜索、寄存器配置校验")
                    print("  - 一般对话: 任何其他问题")
                    print("\n🧠 上下文工程特性:")
                    print("  - 系统会记住你的偏好和重要信息")
                    print("  - 支持多轮连续对话，保持上下文连贯性")
                    print("  - 自动分类保存重要信息到长期记忆")
                    continue
                
                response = await llm_system.chat_with_tools(user_input)
                print(f"🤖 助手: {response}")
                
            except KeyboardInterrupt:
                llm_system.clear_session(save_summary=True)
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