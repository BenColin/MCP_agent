"""
文件工具
提供文件保存功能
"""

import os
from datetime import datetime
from typing import Dict, Any
from mcp.types import TextContent, Tool


class FileTool:
    """文件操作工具类"""
    
    @staticmethod
    def get_tool_definition() -> Tool:
        """获取工具定义"""
        return Tool(
            name="save_outfit_plan",
            description="将穿衣建议内容保存为markdown文件到当前目录",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "要保存的穿衣建议内容（markdown格式）"
                    },
                    "filename": {
                        "type": "string",
                        "description": "保存的markdown文件名，可选，默认为outfit_plan_YYYYMMDD_HHMM.md"
                    }
                },
                "required": ["content"]
            }
        )
    
    @staticmethod
    def handle_save_outfit_plan(arguments: Dict[str, Any]) -> list[TextContent]:
        """
        保存穿衣建议到文件
        
        Args:
            arguments: 包含content和filename参数的字典
            
        Returns:
            包含保存结果的TextContent列表
        """
        try:
            content = arguments.get("content", "")
            if not content:
                return [TextContent(type="text", text="错误：内容不能为空")]
            
            # 生成文件名
            filename = arguments.get("filename")
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = f"outfit_plan_{timestamp}.md"
            
            # 确保文件名以.md结尾
            if not filename.endswith('.md'):
                filename += '.md'
            
            # 保存文件
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 获取文件信息
            file_size = os.path.getsize(filename)
            
            response_text = f"""✅ 穿衣建议已保存成功！

📁 文件名：{filename}
📊 文件大小：{file_size} 字节
📍 保存位置：{os.path.abspath(filename)}
⏰ 保存时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 您可以打开文件查看详细的穿衣建议内容。"""

            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            error_msg = f"保存文件失败: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    @staticmethod
    def save_content_to_file(content: str, filename: str = None) -> str:
        """
        保存内容到文件的便捷方法
        
        Args:
            content: 要保存的内容
            filename: 文件名，可选
            
        Returns:
            保存的文件名
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = f"outfit_plan_{timestamp}.md"
            
            if not filename.endswith('.md'):
                filename += '.md'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filename
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")