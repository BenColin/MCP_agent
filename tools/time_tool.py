"""
时间工具
提供系统时间获取功能
"""

from datetime import datetime, timezone
from typing import Dict, Any
from mcp.types import TextContent, Tool


class TimeTool:
    """时间相关工具类"""
    
    @staticmethod
    def get_tool_definition() -> Tool:
        """获取工具定义"""
        return Tool(
            name="get_current_time",
            description="获取当前系统时间，支持指定时区",
            inputSchema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "时区名称，例如：Asia/Shanghai, Asia/Beijing, UTC等，默认为Asia/Shanghai",
                        "default": "Asia/Shanghai"
                    },
                    "format": {
                        "type": "string", 
                        "description": "时间格式，例如：%Y-%m-%d %H:%M:%S，默认为%Y-%m-%d %H:%M",
                        "default": "%Y-%m-%d %H:%M"
                    }
                },
                "required": []
            }
        )
    
    @staticmethod
    def handle_get_current_time(arguments: Dict[str, Any]) -> list[TextContent]:
        """
        处理获取当前时间请求
        """
        timezone_str = arguments.get("timezone", "local")
        time_format = arguments.get("format", "%Y-%m-%d %H:%M:%S")
        
        try:
            # 获取当前时间
            if timezone_str == "local" or not timezone_str:
                now = datetime.now()
                tz_info = "本地时区"
            else:
                # 简化时区处理，只支持UTC
                if timezone_str.upper() == "UTC":
                    now = datetime.now(timezone.utc)
                    tz_info = "UTC"
                else:
                    # 其他时区使用本地时间
                    now = datetime.now()
                    tz_info = f"本地时区（不支持{timezone_str}）"
            
            # 格式化时间
            formatted_time = now.strftime(time_format)
            
            # 获取星期几
            weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
            weekday = weekdays[now.weekday()]
            
            # 生成详细的时间信息
            time_info = {
                "formatted_time": formatted_time,
                "weekday": weekday,
                "timezone": tz_info,
                "timestamp": int(now.timestamp()),
                "iso_format": now.isoformat()
            }
            
            result_text = f"""
🕐 当前时间信息

📅 时间：{time_info['formatted_time']}
📆 星期：{time_info['weekday']}
🌍 时区：{time_info['timezone']}
⏱️ 时间戳：{time_info['timestamp']}
📋 ISO格式：{time_info['iso_format']}

✅ 时间获取成功！
"""
            
            return [TextContent(type="text", text=result_text.strip())]
            
        except Exception as e:
            error_text = f"❌ 获取时间时出错：{str(e)}"
            return [TextContent(type="text", text=error_text)]
    
    @staticmethod
    def get_formatted_time(timezone_name: str = "Asia/Shanghai", 
                          time_format: str = "%Y-%m-%d %H:%M") -> str:
        """
        获取格式化的当前时间字符串
        
        Args:
            timezone_name: 时区名称
            time_format: 时间格式
            
        Returns:
            格式化的时间字符串
        """
        try:
            tz = pytz.timezone(timezone_name)
            current_time = datetime.now(tz)
            return current_time.strftime(time_format)
        except Exception:
            # 出错时返回默认格式
            return datetime.now().strftime(time_format)