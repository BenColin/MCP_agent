"""
文件系统工具模块
提供文件和目录操作的MCP工具接口
"""

import os
import json
from typing import Dict, Any, List


class FileSystemTool:
    """文件系统工具类，提供文件和目录操作功能"""
    
    def __init__(self):
        self.name = "filesystem"
        self.description = "文件系统操作工具，支持文件读写、目录管理、文件搜索等功能"
    
    def get_tool_definition(self) -> List[Dict[str, Any]]:
        """获取文件系统工具的定义"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "要读取的文件路径"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "写入文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "要写入的文件路径"},
                            "content": {"type": "string", "description": "要写入的内容"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "列出目录内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "要列出的目录路径"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_directory",
                    "description": "创建目录",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "要创建的目录路径"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "搜索文件和目录",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "搜索的根目录"},
                            "pattern": {"type": "string", "description": "搜索模式"},
                            "exclude_patterns": {"type": "array", "items": {"type": "string"}, "description": "排除模式"}
                        },
                        "required": ["path", "pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_file_info",
                    "description": "获取文件或目录信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_file",
                    "description": "移动或重命名文件/目录",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "源文件路径"},
                            "destination": {"type": "string", "description": "目标文件路径"}
                        },
                        "required": ["source", "destination"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "编辑文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"},
                            "old_text": {"type": "string", "description": "要替换的文本"},
                            "new_text": {"type": "string", "description": "新文本"},
                            "dry_run": {"type": "boolean", "description": "是否预览模式", "default": False}
                        },
                        "required": ["path", "old_text", "new_text"]
                    }
                }
            }
        ]
    
    def read_file(self, path: str) -> str:
        """读取文件内容"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"文件内容：\n{content}"
        except Exception as e:
            return f"读取文件失败：{str(e)}"
    
    def write_file(self, path: str, content: str) -> str:
        """写入文件内容"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"文件写入成功：{path}"
        except Exception as e:
            return f"写入文件失败：{str(e)}"
    
    def list_directory(self, path: str) -> str:
        """列出目录内容"""
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    items.append(f"📄 {item} ({size} bytes)")
            
            return f"目录内容 ({path})：\n" + "\n".join(items)
        except Exception as e:
            return f"列出目录失败：{str(e)}"
    
    def create_directory(self, path: str) -> str:
        """创建目录"""
        try:
            os.makedirs(path, exist_ok=True)
            return f"目录创建成功：{path}"
        except Exception as e:
            return f"创建目录失败：{str(e)}"
    
    def search_files(self, path: str, pattern: str, exclude_patterns: List[str] = None) -> str:
        """搜索文件"""
        try:
            exclude_patterns = exclude_patterns or []
            found_files = []
            
            for root, dirs, files in os.walk(path):
                for file in files:
                    if pattern.lower() in file.lower():
                        # 检查是否应该排除
                        should_exclude = any(excl.lower() in file.lower() for excl in exclude_patterns)
                        if not should_exclude:
                            file_path = os.path.join(root, file)
                            found_files.append(file_path)
            
            if found_files:
                return f"找到 {len(found_files)} 个文件：\n" + "\n".join(found_files)
            else:
                return f"未找到匹配 '{pattern}' 的文件"
        except Exception as e:
            return f"搜索文件失败：{str(e)}"
    
    def get_file_info(self, path: str) -> str:
        """获取文件信息"""
        try:
            stat = os.stat(path)
            info = {
                "路径": path,
                "大小": f"{stat.st_size} bytes",
                "修改时间": str(stat.st_mtime),
                "是否目录": os.path.isdir(path)
            }
            return json.dumps(info, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"获取文件信息失败：{str(e)}"
    
    def move_file(self, source: str, destination: str) -> str:
        """移动文件"""
        try:
            import shutil
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            return f"文件移动成功：{source} -> {destination}"
        except Exception as e:
            return f"移动文件失败：{str(e)}"
    
    def edit_file(self, path: str, old_text: str, new_text: str, dry_run: bool = False) -> str:
        """编辑文件内容"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_text not in content:
                return f"未找到要替换的文本：'{old_text}'"
            
            new_content = content.replace(old_text, new_text)
            
            if dry_run:
                return f"预览模式 - 将替换：'{old_text}' -> '{new_text}'"
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return f"文件编辑成功：{path}"
        except Exception as e:
            return f"编辑文件失败：{str(e)}"