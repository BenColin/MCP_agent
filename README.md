# MCP 智能助手 + 上下文工程

基于 MCP (Model Context Protocol) 的多功能智能助手，集成天气查询、文件系统操作、时间获取、AFM工具等，**支持多轮连续对话和智能记忆管理**。

## ✨ 核心特性

### 🧠 上下文工程（Context Engineering）
- **多轮连续对话**: 保持对话连贯性，理解上下文关系
- **智能记忆管理**: 自动识别并保存用户偏好、重要信息
- **短期/长期记忆**: 分层管理对话历史和用户画像
- **上下文窗口优化**: 防止token超限，智能压缩历史消息

### 🛠️ 工具集成
- 📁 **文件系统**: 读写、搜索、编辑、移动文件
- 🌤️ **天气查询**: 支持任意城市和日期
- ⏰ **时间服务**: 多时区、多格式支持
- 🧪 **AFM工具**: 问题查询、寄存器校验、协议检索、语义搜索



## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -e .
```

### 2. 快速体验（推荐）
```bash
# 5分钟了解所有功能
python quick_start.py
```

### 3. 启动交互式对话
```bash
python llm_with_mcp_tools.py
```

**特殊命令**:
- `clear` / `清除` - 清除当前会话记忆
- `status` / `状态` - 查看记忆系统状态
- `help` / `帮助` - 查看可用功能
- `quit` / `退出` - 退出程序（自动保存会话）
### 4. 运行基础工具演示
```bash
# 天气工具演示
python demo_usage.py weather

# 全工具综合演示
python demo_usage.py all

# 交互式对话模式
python demo_usage.py interactive
```

## 💡 使用示例

### 多轮对话示例
```
用户: 你好，我叫小明，是AFM工程师
助手: 你好小明！...
💾 检测到重要信息，已保存到长期记忆（类型: fact）

用户: 我喜欢简洁的回答
助手: 明白了，我会保持简洁。
💾 检测到重要信息，已保存到长期记忆（类型: preference）

用户: 你还记得我叫什么吗？
助手: 你叫小明！（从短期记忆读取）

[新会话]
用户: 我之前告诉过你我的职业吗？
助手: 是的，你是AFM工程师。（从长期记忆读取）
```

### 天气工具 (WeatherTool)
- 支持城市天气查询
- 支持指定日期查询
- 返回详细天气信息

### 文件系统工具 (FileSystemTool)
- `read_file`: 读取文件内容
- `write_file`: 写入文件内容
- `list_directory`: 列出目录内容
- `create_directory`: 创建目录
- `search_files`: 搜索文件
- `get_file_info`: 获取文件信息
- `move_file`: 移动文件
- `edit_file`: 编辑文件内容

### 时间工具 (TimeTool)
- 获取当前时间
- 支持多时区
- 支持多种时间格式

### 文件工具 (FileTool)
- 保存内容到文件
- 自动创建目录
- 支持多种文件格式

### AFM 工具
- `get_afm_prompt`: 返回 AFM助手提示词
- `query_afm_issue`: 查询常见问题（支持分类/编号/关键词）
- `validate_afm_registers`: 校验寄存器配置的类型、范围与步进
- `search_protocol_register`: 检索协议中的寄存器信息
- `search_afm_issue_semantic`: **语义检索**（支持embedding/rerank模型）

## 💡 使用示例

### 🧠 上下文工程示例

```
用户: 你好，我叫小明，我是AFM工程师
助手: 你好小明！很高兴认识你...
💾 检测到重要信息，已保存到长期记忆（类型: fact）

用户: 我喜欢简洁的回答，不要太啰嗦
助手: 明白了，我会保持简洁。
💾 检测到重要信息，已保存到长期记忆（类型: preference）

用户: 你还记得我叫什么名字吗？
助手: 当然记得，你叫小明！

[新会话开始]
用户: 我之前告诉过你我的职业吗？
助手: 是的，你是AFM工程师。（从长期记忆中读取）
```

### 基础功能示例

### 天气查询
```
用户: 北京今天天气怎么样？
助手: [调用天气工具查询并返回结果]
```

### 文件操作
```
用户: 帮我创建一个名为test.txt的文件，内容是"Hello World"
助手: [调用文件系统工具创建文件]
```

### 时间查询
```
用户: 现在几点了？
助手: [调用时间工具获取当前时间]
```

## 🛠️ 技术架构

### 核心架构
- **MCP协议**: 使用标准MCP协议进行工具通信
- **异步处理**: 基于asyncio的高性能异步架构
- **模块化设计**: 每个工具独立模块，易于扩展
- **错误处理**: 完善的异常处理和错误提示
- **类型安全**: 使用类型注解确保代码质量

### 🧠 上下文工程架构

```
用户输入 → Context Engineer → LLM + Tools → 响应 + 记忆更新
           ↓                                      ↓
    [短期记忆 + 长期记忆 + 知识库]  ←───────────────┘
```

**关键组件**:
1. **MemoryManager**: 管理长期记忆（用户画像、会话历史、知识库）
2. **ShortTermMemory**: 管理对话历史和上下文窗口
3. **ContextEngineer**: 动态构建提示、判断记忆保存

**详细架构**: 请查看 [CONTEXT_ENGINEERING_DESIGN.md](CONTEXT_ENGINEERING_DESIGN.md)

## 📝 开发说明

### 使用上下文工程

#### 启用上下文工程（默认）
```python
from llm_with_mcp_tools import LLMWithMCPTools

llm_system = LLMWithMCPTools(
    enable_context_engineering=True,  # 启用上下文工程
    memory_dir="memory"               # 记忆存储目录
)
```

#### 禁用上下文工程（传统模式）
```python
llm_system = LLMWithMCPTools(enable_context_engineering=False)
```

#### 查看记忆状态
```python
status = llm_system.get_memory_status()
print(json.dumps(status, ensure_ascii=False, indent=2))
```

#### 手动清除会话
```python
llm_system.clear_session(save_summary=True)  # 清除并保存摘要
```

### 添加新工具
1. 在 `tools/` 目录下创建新的工具模块
2. 实现工具类，包含 `get_tool_definition()` 方法
3. 在 `mcp_server.py` 中注册新工具（list_tools 和 call_tool 路由）
4. 在 `llm_with_mcp_tools.py` 中添加工具定义（用于 LLM tool calls）

### 🎯 性能与限制

### 上下文工程性能
- **内存占用**: < 5MB（轻量级）
- **记忆加载**: < 10ms
- **上下文构建**: < 50ms
- **支持会话数**: < 50次历史会话
- **知识库条目**: < 1000条（超过建议使用向量数据库）

### 配置参数

在 `context_manager.py` 中可调整:
```python
ShortTermMemory(
    max_messages=20,    # 最大消息数
    max_tokens=4000     # 最大token估算值
)
```

## 🔮 未来规划

- [ ] 集成向量数据库（ChromaDB/FAISS）用于语义检索
- [ ] 实现完整的RAG（检索增强生成）流程
- [ ] 添加记忆图谱（Memory Graph）
- [ ] 支持多模态记忆（图片、文件）
- [ ] 多用户隔离和权限管理
- [ ] 对话主题自动提取和分类

## 📚 文档

- [上下文工程架构设计文档](CONTEXT_ENGINEERING_DESIGN.md) - 详细的架构说明和技术决策

## 配置说明
- API配置在 `llm_with_mcp_tools.py` 中
- 工具配置在各自的工具模块中
- 项目依赖在 `pyproject.toml` 中管理

## 📄 许可证

MIT License