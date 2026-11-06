"""
穿衣建议生成工具
将用户提供的时间、地点、天气、温度等信息，生成详细的markdown穿衣建议
"""

import os
import requests
from typing import Dict, Any, List
from mcp.types import TextContent, Tool


class OutfitTool:
    """穿衣建议生成工具类"""

    API_URL = "https://api.siliconflow.cn/v1/chat/completions"
    DEFAULT_MODEL = "Pro/deepseek-ai/DeepSeek-V3.1-Terminus"

    @staticmethod
    def get_tool_definition() -> Tool:
        """获取MCP工具定义"""
        return Tool(
            name="generate_outfit_plan",
            description="根据时间、地点、天气、温度生成详细的穿衣建议（markdown格式）",
            inputSchema={
                "type": "object",
                "properties": {
                    "time": {"type": "string", "description": "时间，如 '2024-03-15 08:00' 或 '今天'"},
                    "location": {"type": "string", "description": "地点或城市名称，如 '北京'"},
                    "weather": {"type": "string", "description": "天气状况，如 '晴'、'小雨'、'阴'"},
                    "temperature": {"type": "string", "description": "温度信息，如 '12℃-18℃' 或 '15℃'"},
                    "preferences": {"type": "string", "description": "用户偏好或场景，如 '通勤'、'正式场合'、'户外运动'"},
                    "model": {"type": "string", "description": "LLM模型名称，默认 DeepSeek-V3.1-Terminus"},
                    "api_key": {"type": "string", "description": "SiliconFlow API Key（否则使用环境变量 SILICONFLOW_API_KEY）"}
                },
                "required": ["time", "location", "weather", "temperature"]
            }
        )

    @staticmethod
    def get_llm_tool_definition() -> Dict[str, Any]:
        """以LLM tools规范导出定义"""
        return {
            "type": "function",
            "function": {
                "name": "generate_outfit_plan",
                "description": "根据时间、地点、天气、温度生成详细的穿衣建议（markdown格式）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time": {"type": "string", "description": "时间，如 '2024-03-15 08:00' 或 '今天'"},
                        "location": {"type": "string", "description": "地点或城市名称，如 '北京'"},
                        "weather": {"type": "string", "description": "天气状况，如 '晴'、'小雨'、'阴'"},
                        "temperature": {"type": "string", "description": "温度信息，如 '12℃-18℃' 或 '15℃'"},
                        "preferences": {"type": "string", "description": "用户偏好或场景，如 '通勤'、'正式场合'、'户外运动'"},
                        "model": {"type": "string", "description": "LLM模型名称，默认 DeepSeek-V3.1-Terminus"},
                        "api_key": {"type": "string", "description": "SiliconFlow API Key（否则使用环境变量 SILICONFLOW_API_KEY）"}
                    },
                    "required": ["time", "location", "weather", "temperature"]
                }
            }
        }

    @staticmethod
    def _compose_prompt(time: str, location: str, weather: str, temperature: str, preferences: str | None) -> List[Dict[str, str]]:
        """生成对话消息列表"""
        sys_prompt = (
            "你是一位专业的时尚顾问和穿衣搭配专家，擅长根据天气、时间和场合提供实用建议。"
            "输出必须是结构化、详细的markdown文档，避免空话套话。"
        )

        user_prompt = f"""请根据以下信息生成详细的穿衣建议，以markdown格式输出：

**基本信息：**
- 时间：{time}
- 地点：{location}
- 天气：{weather}
- 温度：{temperature}
{f'- 偏好/场景：{preferences}\n' if preferences else ''}

请生成一份实用、具体的建议，包含：
1. 基本信息总结
2. 上身搭配建议
3. 下身搭配建议
4. 鞋履选择指导
5. 帽子/配饰建议
6. 外套推荐
7. 贴心提示（如备选方案、穿脱层次、是否携带雨具等）
8. 注意事项（温差、风力、降雨概率、紫外线强度等）

要求：
- 结合季节、温度区间、天气状况和时段因素
- 给出明确的材质/款式/色彩方向建议，而非泛泛而谈
- 使用二级/三级标题组织内容，便于阅读
- 以markdown文档完整输出（包含标题、分节、列表）
"""

        return [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ]

    @staticmethod
    def handle_generate_outfit_plan(arguments: Dict[str, Any]) -> list[TextContent]:
        """调用LLM生成穿衣建议（markdown）"""
        try:
            time = arguments.get("time")
            location = arguments.get("location")
            weather = arguments.get("weather")
            temperature = arguments.get("temperature")
            preferences = arguments.get("preferences")

            if not all([time, location, weather, temperature]):
                return [TextContent(type="text", text="错误：缺少必要参数 time/location/weather/temperature")]

            api_key = arguments.get("api_key") or os.environ.get("SILICONFLOW_API_KEY")
            if not api_key:
                return [TextContent(type="text", text="错误：未提供API Key。请在参数中传入 api_key 或配置环境变量 SILICONFLOW_API_KEY。")]

            model = arguments.get("model") or OutfitTool.DEFAULT_MODEL
            messages = OutfitTool._compose_prompt(time, location, weather, temperature, preferences)

            payload = {
                "model": model,
                "messages": messages,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            resp = requests.post(OutfitTool.API_URL, json=payload, headers=headers, timeout=60)
            data = resp.json()

            if resp.status_code != 200:
                err = data.get("error", {}).get("message", f"HTTP {resp.status_code}")
                return [TextContent(type="text", text=f"API调用失败：{err}")]

            if "choices" not in data or not data["choices"]:
                return [TextContent(type="text", text="API返回内容为空，无法生成建议")]

            content = data["choices"][0]["message"].get("content", "")
            if not content:
                return [TextContent(type="text", text="LLM未返回内容")]

            return [TextContent(type="text", text=content)]

        except requests.exceptions.RequestException as e:
            return [TextContent(type="text", text=f"网络请求失败：{str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"生成穿衣建议失败：{str(e)}")]