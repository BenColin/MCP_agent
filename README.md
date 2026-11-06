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
- 🌤️ **天气查询**。按城市返回内置的模拟天气
- ⏰ **时间服务**: 多时区、多格式支持
- 🧪 **AFM工具**: 问题查询、寄存器校验、协议检索、语义搜索



## 🚀 配置与运行

在所选版本的仓库根目录执行下文的 PowerShell 命令。

| 快照 | MCP 服务脚本 | AFM 数据目录 |
| --- | --- | --- |
| V0.1（`1222c2d`） | `mcp_tools_server.py` | `AFM_tool/` |
| V0.3（`24be745`） | `mcp_server.py` | `Context/` |

### 1. 安装 Python 和依赖

复现两版时统一使用 **Python 3.12**。`tools/outfit_tool.py` 的 f-string 用到了 3.12 的语法。安装时启用 Windows 的 `py` 启动器，再用 `py -3.12 --version` 确认解释器版本。 [Python 3.12 语法说明](https://docs.python.org/3.12/whatsnew/3.12.html#pep-701-syntactic-formalization-of-f-strings)

两版都把运行依赖写在 `pyproject.toml` 的 Hatch 构建表下。请在仓库外创建虚拟环境，显式安装 MCP Python SDK 1.x（工具协议）、`requests`（HTTP 请求）和 `pydantic`（MCP 数据模型）。 [Python 项目依赖规范](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#dependencies-and-requirements)

```powershell
$agentVenv = Join-Path $env:LOCALAPPDATA 'MCP_agent\venv312'
py -3.12 -m venv $agentVenv
$agentPython = Join-Path $agentVenv 'Scripts\python.exe'
& $agentPython -m pip install "mcp>=1.0.0,<2" "requests>=2.31.0" "pydantic>=2.5.0,<3"
& $agentPython -m pip check
```

`hatchling` 用于项目打包。`pytest`、`pytest-asyncio`、`black` 和 `flake8` 是开发可选依赖。

### 2. 驱动和本地文件

- **驱动**。两版直接读取仓库内的 AFM 协议字典、提示词和故障文档，用于查询和数值校验，无需安装 AFM 硬件驱动。
- **V0.1 启动缺件**。客户端和服务端都导入了 `tools/outfit_tool.py`，该文件从 V0.3 起入库。在单独检出的 V0.1 工作副本中执行 `git restore --source=24be745 --worktree -- tools/outfit_tool.py`，即可从 V0.3 补齐该模块。
- **V0.3 记忆数据**。常规会话默认使用 `memory/`，快速演示使用 `quick_start_memory/`。程序自动创建目录，运行位置须可写。

### 3. 配置硅基流动 API

主对话、穿衣建议和 AFM 语义检索共用一把硅基流动中国站 API Key。天气工具读取内置模拟数据，`demo_usage.py weather` 仍会通过主对话请求模型。

在控制台创建密钥，在下面的隐藏输入提示中输入裸密钥，供当前 PowerShell 会话使用。第二条命令查询账户可用的模型 ID。 [硅基流动 API 密钥](https://cloud.siliconflow.cn/account/ak) · [模型列表接口](https://docs.siliconflow.cn/docs/api/models-get)

```powershell
$env:SILICONFLOW_API_KEY = [pscredential]::new('SiliconFlow', (Read-Host 'SiliconFlow API Key' -AsSecureString)).GetNetworkCredential().Password
(Invoke-RestMethod -Uri 'https://api.siliconflow.cn/v1/models' -Headers @{
    Authorization = "Bearer $env:SILICONFLOW_API_KEY"
}).data.id
```

**主对话和 MCP 子进程（两版）**。在本地工作副本的 `llm_with_mcp_tools.py` 中补齐 `import os`、`import sys`，并从 `mcp.client.stdio` 导入 `get_default_environment`。在构造函数中用 `self.api_key = os.environ.get("SILICONFLOW_API_KEY", "")` 替换占位符赋值，再在 `initialize_mcp()` 中按下方构造参数。V0.1 将脚本名换为 `mcp_tools_server.py`。穿衣工具会从子进程环境读取密钥。 [MCP SDK 的 stdio 环境传递](https://github.com/modelcontextprotocol/python-sdk/blob/v1.0.0/src/mcp/client/stdio.py)

```python
server_params = StdioServerParameters(
    command=sys.executable,
    args=[os.path.join(current_dir, "mcp_server.py")],
    env={**get_default_environment(), "SILICONFLOW_API_KEY": self.api_key},
)
```

两版的主对话及穿衣工具默认使用 `Pro/deepseek-ai/DeepSeek-V3.1-Terminus`。若需换模型，用账户可用且支持工具调用的模型 ID 更新 `llm_with_mcp_tools.py` 的 `self.model` 和 `tools/outfit_tool.py` 的 `DEFAULT_MODEL`。

**可选联网功能**。请求头统一使用 `Bearer` 格式，环境变量仍保存裸密钥。 [Embedding 接口](https://docs.siliconflow.cn/docs/api/embeddings-post) · [Rerank 接口](https://docs.siliconflow.cn/docs/api/rerank-post)

- **AFM 语义检索**。V0.1 在 `tools/afm_tool.py` 的 `_sf_headers()` 中配置，V0.3 在 `tools/afm_semantic_tool.py` 的 `_rerank()`、`_embedding_scores()` 中配置。将各处的 `"Authorization": api_key` 改为 `"Authorization": f"Bearer {api_key}"`。默认模型分别为 `Qwen/Qwen3-Embedding-8B` 和 `Qwen/Qwen3-Reranker-8B`。
- **知识库重排（V0.3）**。使用 `search_knowledge(..., use_rerank=True)` 时，将 `context_manager.py` 的 `_rerank_results()` 中的请求头改为 `"Authorization": f"Bearer {os.environ['SILICONFLOW_API_KEY']}"`。
- **独立 API 示例**。V0.1 用 `siliconCloud.py`，V0.3 用 `Context/请求siliconCloud示例.py`。在文件顶部加 `import os`，将各处 `Authorization` 占位符改为上一条的环境变量写法。

### 4. 启动

完成主对话配置后，从当前会话按需运行。

```powershell
& $agentPython .\llm_with_mcp_tools.py  # 两版的交互对话
& $agentPython .\demo_usage.py weather  # 两版也支持 all 和 interactive
& $agentPython .\demo_usage.py afm      # 仅 V0.1
& $agentPython .\quick_start.py         # 仅 V0.3
```

V0.3 的交互命令包括 `clear`（清除会话）、`status`（记忆状态）、`help`（帮助）、`quit`（退出）。

接入独立 MCP 客户端时，`command` 填虚拟环境中 Python 的绝对路径，`args` 传对应服务脚本的绝对路径。联网工具需要在服务的 `env` 中注入 `SILICONFLOW_API_KEY`。本地 AFM 查询、时间、文件和模拟天气工具可直接调用。

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
- 按城市返回内置的模拟天气数据

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

## 📄 许可证

MIT License