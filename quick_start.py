#!/usr/bin/env python3
"""
上下文工程快速入门 - 5分钟了解多轮对话和记忆管理

演示内容：
1. 创建启用上下文工程的LLM系统
2. 进行多轮对话（用户信息、偏好设置、工具调用）
3. 测试短期记忆（对话历史回顾）
4. 查看记忆系统状态
5. 测试长期记忆持久化（新会话中回顾之前的信息）
"""

import asyncio
from llm_with_mcp_tools import LLMWithMCPTools


async def quick_start():
    """快速入门演示 - 展示上下文工程的核心功能"""
    
    # ====================
    # 第1步：创建启用上下文工程的LLM系统
    # ====================
    print("🚀 步骤1：创建LLM系统（启用上下文工程）")
    llm_system = LLMWithMCPTools(
        enable_context_engineering=True,  # 启用记忆功能
        memory_dir="quick_start_memory"   # 指定记忆存储目录
    )
    
    try:
        # ====================
        # 第2步：初始化MCP工具
        # ====================
        print("\n🔧 步骤2：初始化MCP工具...")
        await llm_system.initialize_mcp()
        print("✅ 工具初始化完成!\n")
        
        # ====================
        # 第3步：多轮对话演示
        # ====================
        print("💬 步骤3：开始多轮对话（展示记忆功能）")
        print("="*60)
        
        # 第1轮：用户提供个人信息（应被识别为重要事实）
        print("\n【第1轮】用户提供个人信息")
        response1 = await llm_system.chat_with_tools("你好，我叫张三，是一名软件工程师")
        print(f"助手: {response1}")
        
        # 第2轮：设置偏好（应被识别为用户偏好）
        print("\n【第2轮】用户设置偏好")
        response2 = await llm_system.chat_with_tools("我喜欢简洁明了的回答")
        print(f"助手: {response2}")
        
        # 第3轮：实际任务 - 天气查询（测试工具调用）
        print("\n【第3轮】实际任务 - 天气查询")
        response3 = await llm_system.chat_with_tools("北京今天天气怎么样？")
        print(f"助手: {response3}")
        
        # 第4轮：测试短期记忆（回顾之前的信息）
        print("\n【第4轮】测试短期记忆")
        response4 = await llm_system.chat_with_tools("你还记得我叫什么名字吗？")
        print(f"助手: {response4}")
        
        # 第五轮：测试职业记忆
        print("\n【第5轮】测试职业记忆")
        response5 = await llm_system.chat_with_tools("我刚才说过我的职业吗？")
        print(f"助手: {response5}")
        
        # 第四步：查看记忆状态
        print("\n" + "="*60)
        print("📊 步骤4：查看记忆系统状态")
        status = llm_system.get_memory_status()
        print(f"  - 短期记忆消息数: {status['short_term_messages']}")
        print(f"  - 用户名: {status['user_profile']['name']}")
        print(f"  - 偏好设置数: {status['user_profile']['preferences_count']}")
        print(f"  - 重要事实数: {status['user_profile']['important_facts_count']}")
        
        # 第五步：清除会话并保存
        print("\n📦 步骤5：清除会话并保存到长期记忆")
        llm_system.clear_session(save_summary=True)
        
        # ====================
        # 第6步：模拟新会话，测试长期记忆持久化
        # ====================
        print("\n" + "="*60)
        print("🔄 步骤6：模拟新会话（测试长期记忆持久化）")
        print("="*60)
        
        # 创建新的LLM系统实例（模拟新会话）
        new_llm_system = LLMWithMCPTools(
            enable_context_engineering=True,
            memory_dir="quick_start_memory"  # 使用相同的记忆目录
        )
        await new_llm_system.initialize_mcp()
        
        print("\n【新会话 - 第1轮】测试长期记忆（系统应能从之前的会话中回忆起信息）")
        response_new = await new_llm_system.chat_with_tools(
            "你还记得我的名字和职业吗？（这是一个新的会话）"
        )
        print(f"助手: {response_new}")
        
        # 清理新会话
        await new_llm_system.cleanup_mcp()
        
        # ====================
        # 总结
        # ====================
        print("\n" + "="*60)
        print("✅ 快速入门完成！")
        print("\n📚 你已经学会了:")
        print("  1. 创建启用上下文工程的LLM系统")
        print("  2. 进行多轮连续对话")
        print("  3. 系统自动记忆用户信息和偏好")
        print("  4. 查看记忆系统状态")
        print("  5. 保存和加载长期记忆（跨会话）")
        print("\n💡 下一步:")
        print("  - 运行 'python llm_with_mcp_tools.py' 开始自由对话")
        print("  - 查看 'README.md' 了解更多功能")
        print("  - 探索其他MCP工具（天气、文件、AFM等）")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await llm_system.cleanup_mcp()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🌟 上下文工程快速入门")
    print("  5分钟了解多轮对话和记忆管理")
    print("="*60 + "\n")
    
    asyncio.run(quick_start())
