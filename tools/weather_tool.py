"""
天气工具
提供天气查询功能
"""

import requests
from typing import Dict, Any
from mcp.types import TextContent, Tool


class WeatherTool:
    """天气查询工具类"""
    
    @staticmethod
    def get_tool_definition() -> Tool:
        """获取工具定义"""
        return Tool(
            name="get_weather",
            description="获取指定城市的当前天气信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海、广州等"
                    }
                },
                "required": ["city"]
            }
        )

    @staticmethod
    def get_llm_tool_definition() -> dict:
        """以LLM工具规范导出定义，用于 tools 参数"""
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取指定城市的当前天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，例如：北京、上海、广州等"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    
    @staticmethod
    def handle_get_weather(arguments: Dict[str, Any]) -> list[TextContent]:
        """
        获取天气信息
        
        Args:
            arguments: 包含city参数的字典
            
        Returns:
            包含天气信息的TextContent列表
        """
        try:
            city = arguments.get("city", "")
            if not city:
                return [TextContent(type="text", text="错误：请提供城市名称")]
            
            # 模拟天气API调用
            # 在实际应用中，这里应该调用真实的天气API
            weather_data = WeatherTool._get_mock_weather_data(city)
            
            response_text = f"""🌤️ {city}天气信息：

📍 城市：{weather_data['city']}
🌡️ 温度：{weather_data['temperature']}
☁️ 天气：{weather_data['weather']}
💨 风力：{weather_data['wind']}
💧 湿度：{weather_data['humidity']}
👁️ 能见度：{weather_data['visibility']}
🌅 日出：{weather_data['sunrise']}
🌇 日落：{weather_data['sunset']}

📝 天气描述：{weather_data['description']}"""

            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            error_msg = f"获取天气信息失败: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    @staticmethod
    def _get_mock_weather_data(city: str) -> Dict[str, str]:
        """
        获取模拟天气数据
        在实际应用中应该替换为真实的天气API调用
        """
        # 模拟不同城市的天气数据
        mock_data = {
            "北京": {
                "city": "北京",
                "temperature": "-2°C",
                "weather": "晴天",
                "wind": "北风3级",
                "humidity": "45%",
                "visibility": "10km",
                "sunrise": "07:25",
                "sunset": "17:15",
                "description": "今日天气晴朗，气温较低，请注意保暖"
            },
            "上海": {
                "city": "上海", 
                "temperature": "8°C",
                "weather": "多云",
                "wind": "东南风2级",
                "humidity": "65%",
                "visibility": "8km",
                "sunrise": "06:45",
                "sunset": "17:30",
                "description": "多云天气，温度适中，适合外出活动"
            },
            "广州": {
                "city": "广州",
                "temperature": "22°C", 
                "weather": "小雨",
                "wind": "南风1级",
                "humidity": "80%",
                "visibility": "5km",
                "sunrise": "06:55",
                "sunset": "18:10",
                "description": "有小雨，湿度较高，出行请携带雨具"
            }
        }
        
        # 如果城市不在预设数据中，返回默认数据
        return mock_data.get(city, {
            "city": city,
            "temperature": "15°C",
            "weather": "多云",
            "wind": "微风",
            "humidity": "60%",
            "visibility": "10km", 
            "sunrise": "06:30",
            "sunset": "18:00",
            "description": f"{city}天气信息暂时无法获取，显示默认数据"
        })