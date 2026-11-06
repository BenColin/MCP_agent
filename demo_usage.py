#!/usr/bin/env python3
"""
LLM + MCP 工具使用示例
展示如何使用集成的LLM和MCP工具系统
"""

import asyncio
from llm_with_mcp_tools import LLMWithMCPTools

async def demo_weather_queries():
    """演示天气查询功能"""
    llm_system = LLMWithMCPTools()
    try:
        print("🌤️ LLM + MCP 天气查询系统演示\n" + "="*50)
        print("🚀 正在启动系统...")
        await llm_system.initialize_mcp()
        print("✅ 系统启动完成!\n")
        
        for i, query in enumerate(["你好，我想知道北京明天的天气怎么样？", 
                                    "请帮我查询2024年3月15日上海的天气情况",
                                    "深圳今天（2024年1月10日）适合户外运动吗？"], 1):
            print(f"\n📝 查询 {i}: {query}\n" + "-"*40)
            try:
                print(f"🤖 回答: {await llm_system.chat_with_tools(query)}\n")
            except Exception as e:
                print(f"❌ 查询失败: {e}\n")
    except Exception as e:
        print(f"❌ 演示失败: {e}")
    finally:
        await llm_system.cleanup_mcp()

async def interactive_mode():
    """交互式对话模式"""
    llm_system = LLMWithMCPTools()
    
    try:
        print("🤖 LLM + MCP 交互式对话模式")
        print("=" * 50)
        print("💡 提示: 输入 'quit' 或 'exit' 退出")
        print("💡 提示: 输入 'help' 查看可用功能")
        print()
        
        # 初始化系统
        print("🚀 正在启动系统...")
        await llm_system.initialize_mcp()
        print("✅ 系统启动完成!\n")
        
        while True:
            try:
                user_input = input("👤 您: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见!")
                    break
                
                if user_input.lower() == 'help':
                    print("🔧 可用功能:")
                    print("  - 天气查询: 询问任何城市的天气情况")
                    print("  - 文件操作: 读写文件、创建目录等")
                    print("  - 时间查询: 获取当前时间")
                    print("  - 穿衣建议: 输入时间/地点/天气/温度生成markdown方案，可保存为md")
                    print("  - AFM工具: 语义检索常见问题、协议寄存器搜索、寄存器配置校验")
                    print("  - 一般对话: 任何其他问题")
                    continue
                
                if not user_input:
                    continue
                
                print("🤖 正在思考...")
                response = await llm_system.chat_with_tools(user_input)
                print(f"🤖 助手: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 处理失败: {e}\n")
    
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
    finally:
        await llm_system.cleanup_mcp()

async def demo_all_tools():
    """演示所有工具的综合功能"""
    llm_system = LLMWithMCPTools()
    try:
        print("🛠️ LLM + MCP 全工具演示\n" + "="*50)
        print("🚀 正在启动系统...")
        await llm_system.initialize_mcp()
        print("✅ 系统启动完成!\n")
        
        for i, query in enumerate(["现在几点了？", 
                                    "帮我创建一个名为test.txt的文件，内容是'Hello World'",
                                    "北京今天天气怎么样？", "读取刚才创建的test.txt文件内容",
                                    "根据今天上海小雨、12℃-16℃生成通勤穿衣建议，并保存为md",
                                    "AFM扫描出现'Z轴无法回零'怎么处理？",
                                    "若调整PFM积分增益，我应该调整哪个寄存器？"], 1):
            print(f"\n📝 演示 {i}: {query}\n" + "-"*40)
            try:
                print(f"🤖 回答: {await llm_system.chat_with_tools(query)}")
            except Exception as e:
                print(f"❌ 执行失败: {e}")
    except Exception as e:
        print(f"❌ 演示失败: {e}")
    finally:
        await llm_system.cleanup_mcp()

async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'weather':
            await demo_weather_queries()
        elif mode == 'all':
            await demo_all_tools()
        elif mode == 'interactive':
            await interactive_mode()
        else:
            print("❌ 未知模式，支持的模式: weather, all, interactive")
    else:
        # 交互式选择模式
        print("🚀 LLM + MCP 工具演示系统")
        print("=" * 50)
        print("请选择演示模式:")
        print("1. 天气工具演示 (weather)")
        print("2. 全工具综合演示 (all)")
        print("3. 交互式对话模式 (interactive)")
        print()
        
        while True:
            choice = input("请输入选择 (1-3): ").strip()
            
            if choice == '1':
                await demo_weather_queries()
                break
            elif choice == '2':
                await demo_all_tools()
                break
            elif choice == '3':
                await interactive_mode()
                break
            else:
                print("❌ 无效选择，请输入 1-3")

if __name__ == "__main__":
    asyncio.run(main())