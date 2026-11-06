# MCP 多功能智能助手

这是一个基于 MCP (Model Context Protocol) 的多功能智能助手项目，集成了天气查询、文件系统操作、时间获取等多种工具，通过LLM实现智能对话和任务执行。

## 🌟 功能特性

- 🌤️ **天气查询**: 支持任意城市和日期的天气信息查询
- 📁 **文件系统操作**: 文件读写、目录管理、文件搜索等完整文件操作
- ⏰ **时间服务**: 获取当前时间，支持多时区和格式
- 💾 **文件保存**: 智能内容保存和管理
- 🤖 **智能对话**: 基于LLM的自然语言交互
- ⚡ **异步架构**: 高性能异步处理
- 🛠️ **模块化设计**: 清晰的工具模块结构
- 🔬 **AFM 控制辅助**: 寄存器查询、标准流程、故障检索（支持嵌入与重排）

## 📁 项目结构
```
MCP_agent/
├── README.md                   # 项目说明文档
├── demo_usage.py              # 演示脚本（支持多种模式）
├── llm_with_mcp_tools.py      # LLM 与 MCP 工具集成核心（交互）
├── mcp_tools_server.py        # MCP 服务器（多工具注册与分发）
├── pyproject.toml             # 项目配置文件
├── AFM_tool/                  # AFM 协议与数据
│   └── 通讯协议V37.py        # AFM 协议寄存器字典
│   ├── AFM助手提示词.md           # AFM 模式标准流程描述
│   └── AFM扫描常见问题及解决.md    # AFM 故障检索知识库
└── tools/                     # 工具模块目录
    ├── __init__.py
    ├── afm_tool.py           # AFM 辅助工具（寄存器/流程/检索）
    ├── outfit_tool.py        # 穿衣建议生成工具（Markdown 输出）
    ├── file_tool.py          # 文件保存工具（保存 Markdown 文档）
    ├── filesystem_tool.py    # 文件系统操作工具（读写/目录/搜索/编辑）
    ├── time_tool.py          # 时间获取工具
    └── weather_tool.py       # 天气查询工具
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 运行演示

#### 方式一：命令行参数
```bash
# 天气工具演示
python demo_usage.py weather

# 全工具综合演示
python demo_usage.py all

# 交互式对话模式
python demo_usage.py interactive

# AFM 工具演示
python demo_usage.py afm
```

#### 方式二：交互式选择
```bash
python demo_usage.py
```

## 🔧 工具说明

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

### AFM 工具 (AFMTool)
- `afm_list_registers`: 按类型/名称/地址列出寄存器，支持 `limit`
- `afm_get_register_info`: 查询单个寄存器详情，如 `REG0B`
- `afm_validate_register_value`: 校验写入值是否符合范围/步长/类型
- `afm_get_mode_standard_flow`: 返回模式标准流程（如“轻敲”“接触”“PFM”等）
- `afm_search_troubleshooting`: 检索常见问题与解决建议（支持嵌入与重排）

示例：
```
# 寄存器列表（开关类，限制返回5条）
afm_list_registers(type="switch", limit=5)

# 寄存器详情
afm_get_register_info(reg="REG0B")

# 写入校验
afm_validate_register_value(reg="REG0B", value=0)

# 模式流程
afm_get_mode_standard_flow(mode="轻敲")

# 故障检索（嵌入+重排）
afm_search_troubleshooting(query="共振峰", category="曲线测试类", limit=5)
```

### SiliconFlow 嵌入与重排配置
- AFM 故障检索可使用 SiliconFlow 的 `embedding` 与 `rerank` 优化复杂字符匹配
- 参考 `/c:/Users/20599/Desktop/MCP_agent/siliconCloud.py`
- 配置环境变量 `SILICONFLOW_API_KEY` 即可启用；未配置时回退为关键词检索

在 Windows PowerShell 设置当前会话：
```
$env:SILICONFLOW_API_KEY = "你的API密钥"
```

或永久设置：
```
setx SILICONFLOW_API_KEY "你的API密钥"
```

## 💡 使用示例

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

- **MCP协议**: 使用标准MCP协议进行工具通信
- **异步处理**: 基于asyncio的高性能异步架构
- **模块化设计**: 每个工具独立模块，易于扩展
- **错误处理**: 完善的异常处理和错误提示
- **类型安全**: 使用类型注解确保代码质量

## 📝 开发说明

### 添加新工具
1. 在 `tools/` 目录下创建新的工具模块
2. 实现工具类，包含 `get_tool_definition()` 方法（返回 MCP `Tool` 或函数式工具定义集合）
3. 在 `mcp_tools_server.py` 中注册工具：
   - 在 `@server.list_tools()` 中加入工具定义（必要时展开函数式列表）
   - 在 `@server.call_tool()` 中分发具体工具处理方法
4. 在 `llm_with_mcp_tools.py` 的 `get_tools_definition()` 中汇总工具定义供 LLM 使用

### 配置说明
- API 配置在 `llm_with_mcp_tools.py` 中（SiliconFlow Chat Completions）
- 工具注册在 `mcp_tools_server.py` 中；工具定义由各自模块提供
- 客户端会统一从工具模块生成 LLM `tools` 参数
- 项目依赖在 `pyproject.toml` 中管理
- AFM 相关数据来源：`AFM_tool/通讯协议V37.py`、`AFM助手提示词.md`、`AFM扫描常见问题及解决.md`

## 📄 许可证

MIT License