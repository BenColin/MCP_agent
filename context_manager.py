#!/usr/bin/env python3
"""
上下文管理器 - Context Engineering
负责管理短期记忆、长期记忆、动态构建提示以及上下文窗口优化

核心功能：
1. MemoryManager - 长期记忆管理（用户画像、会话历史、知识库）
2. ShortTermMemory - 短期记忆管理（对话历史、上下文压缩）
3. ContextEngineer - 上下文工程师（动态提示构建、记忆决策）
"""

import json
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class MemoryManager:
    """记忆管理器 - 管理长期记忆的存储与检索
    
    存储结构：
    - user_profile.json: 用户画像（姓名、偏好、重要事实）
    - session_history.json: 会话历史（最近50次会话摘要）
    - knowledge_base.json: 知识库（领域知识、FAQ等）
    """
    
    def __init__(self, memory_dir: str = "memory"):
        """
        初始化记忆管理器
        
        Args:
            memory_dir: 记忆存储目录（默认: memory/）
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # 长期记忆文件路径
        self.user_profile_path = self.memory_dir / "user_profile.json"
        self.session_history_path = self.memory_dir / "session_history.json"
        self.knowledge_base_path = self.memory_dir / "knowledge_base.json"
        
        # 加载或初始化记忆
        self.user_profile = self._load_json(self.user_profile_path, {
            "name": None,
            "preferences": {},
            "important_facts": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        
        self.session_history = self._load_json(self.session_history_path, {
            "sessions": [],
            "total_conversations": 0
        })
        
        self.knowledge_base = self._load_json(self.knowledge_base_path, {
            "facts": [],
            "entities": {},
            "relationships": []
        })
    
    def _load_json(self, path: Path, default: Dict) -> Dict:
        """加载JSON文件"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载记忆文件失败 {path}: {e}")
        return default
    
    def _save_json(self, path: Path, data: Dict):
        """保存JSON文件"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存记忆文件失败 {path}: {e}")
    
    def update_user_profile(self, key: str, value: Any):
        """更新用户画像"""
        if key == "preferences":
            self.user_profile["preferences"].update(value)
        elif key == "important_facts":
            if value not in self.user_profile["important_facts"]:
                self.user_profile["important_facts"].append(value)
        else:
            self.user_profile[key] = value
        
        self.user_profile["updated_at"] = datetime.now().isoformat()
        self._save_json(self.user_profile_path, self.user_profile)
    
    def get_user_context(self) -> str:
        """获取用户上下文摘要"""
        context_parts = []
        
        if self.user_profile.get("name"):
            context_parts.append(f"用户名: {self.user_profile['name']}")
        
        if self.user_profile["preferences"]:
            prefs = ", ".join([f"{k}: {v}" for k, v in self.user_profile["preferences"].items()])
            context_parts.append(f"用户偏好: {prefs}")
        
        if self.user_profile["important_facts"]:
            facts = "; ".join(self.user_profile["important_facts"][:3])
            context_parts.append(f"重要信息: {facts}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def save_session(self, session_data: Dict):
        """保存会话记录"""
        self.session_history["sessions"].append({
            "timestamp": datetime.now().isoformat(),
            "summary": session_data.get("summary", ""),
            "key_topics": session_data.get("key_topics", []),
            "tools_used": session_data.get("tools_used", [])
        })
        self.session_history["total_conversations"] += 1
        
        # 只保留最近50次会话
        if len(self.session_history["sessions"]) > 50:
            self.session_history["sessions"] = self.session_history["sessions"][-50:]
        
        self._save_json(self.session_history_path, self.session_history)
    
    def add_knowledge(self, fact: str, category: str = "general"):
        """添加知识到知识库"""
        self.knowledge_base["facts"].append({
            "content": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制知识库大小
        if len(self.knowledge_base["facts"]) > 100:
            self.knowledge_base["facts"] = self.knowledge_base["facts"][-100:]
        
        self._save_json(self.knowledge_base_path, self.knowledge_base)
    
    def search_knowledge(self, query: str, top_k: int = 3, use_rerank: bool = False) -> List[str]:
        """知识检索（支持关键词匹配或语义rerank）
        
        Args:
            query: 查询语句
            top_k: 返回结果数量
            use_rerank: 是否使用rerank模型进行语义重排（需要API密钥）
        """
        results = []
        query_lower = query.lower()
        
        # 基础关键词匹配
        for fact in self.knowledge_base["facts"]:
            if query_lower in fact["content"].lower():
                results.append(fact["content"])
        
        # 如果启用rerank且有足够候选项，调用语义重排
        if use_rerank and len(results) > top_k:
            results = self._rerank_results(query, results, top_k)
        else:
            results = results[:top_k]
        
        return results
    
    def _rerank_results(self, query: str, documents: List[str], top_k: int) -> List[str]:
        """使用SiliconFlow的rerank模型进行语义重排"""
        try:
            url = "https://api.siliconflow.cn/v1/rerank"
            payload = {
                "model": "Qwen/Qwen3-Reranker-8B",
                "query": query,
                "documents": documents,
                "top_n": top_k
            }
            headers = {
                "Authorization": "Bearer YOUR_SILICONFLOW_API_KEY",
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # 按相关性分数排序并返回文档
                ranked = sorted(data.get("results", []), key=lambda x: x.get("relevance_score", 0), reverse=True)
                return [documents[item["index"]] for item in ranked[:top_k]]
        except Exception as e:
            print(f"⚠️ Rerank失败，回退到关键词匹配: {e}")
        
        # 失败时回退到简单截取
        return documents[:top_k]


class ShortTermMemory:
    """短期记忆 - 管理当前对话会话的消息历史
    
    功能：
    - 维护对话历史（用户消息、助手回复、工具调用）
    - 自动压缩上下文窗口（防止token超限）
    - 生成会话摘要供长期记忆保存
    """
    
    def __init__(self, max_messages: int = 20, max_tokens: int = 4000):
        """
        初始化短期记忆
        
        Args:
            max_messages: 最大消息数量（默认20条，超出自动压缩）
            max_tokens: 估算的最大token数（默认4000，字符数÷2估算）
        """
        self.messages: List[Dict] = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens
    
    def add_message(self, role: str, content: str, **kwargs):
        """添加消息到短期记忆"""
        message = {"role": role, "content": content}
        message.update(kwargs)
        self.messages.append(message)
        
        # 触发压缩检查
        self._check_and_compress()
    
    def get_messages(self) -> List[Dict]:
        """获取所有消息"""
        return self.messages.copy()
    
    def clear(self):
        """清空短期记忆"""
        self.messages.clear()
    
    def _estimate_tokens(self) -> int:
        """估算当前消息的token数（简化：按字符数 / 2）"""
        total_chars = sum(len(str(msg.get("content", ""))) for msg in self.messages)
        return total_chars // 2
    
    def _check_and_compress(self):
        """检查并压缩记忆（保留系统消息和最近的用户/助手消息）"""
        if len(self.messages) > self.max_messages:
            system_msgs = [msg for msg in self.messages if msg.get("role") == "system"]
            non_system_msgs = [msg for msg in self.messages if msg.get("role") != "system"]
            remaining_space = self.max_messages - len(system_msgs)
            self.messages = system_msgs + (non_system_msgs[-remaining_space:] if remaining_space > 0 else [])
        
        if self._estimate_tokens() > self.max_tokens:
            system_msgs = [msg for msg in self.messages if msg.get("role") == "system"]
            non_system_msgs = [msg for msg in self.messages if msg.get("role") != "system"]
            remaining_space = max(1, (self.max_messages - len(system_msgs)) // 2)
            self.messages = system_msgs + (non_system_msgs[-remaining_space:] if remaining_space > 0 else [])
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要（用于保存到长期记忆）"""
        user_messages = [msg for msg in self.messages if msg.get("role") == "user"]
        topics = []
        for msg in user_messages[:5]:
            topics.extend(msg.get("content", "").split()[:5])
        
        return {
            "summary": f"共 {len(user_messages)} 轮对话",
            "key_topics": list(set(topics))[:10],
            "tools_used": self._extract_tools_used()
        }
    
    def _extract_tools_used(self) -> List[str]:
        """提取本次会话使用的工具"""
        tools = set()
        for msg in self.messages:
            if msg.get("role") == "tool":
                tools.add("tool_call")
            if msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    tools.add(tool_call.get("function", {}).get("name", "unknown"))
        return list(tools)


class ContextEngineer:
    """上下文工程师 - 动态构建提示并管理上下文
    
    核心职责：
    1. 整合短期记忆（对话历史）和长期记忆（用户画像）
    2. 动态构建包含完整上下文的系统提示
    3. 智能判断哪些信息应保存到长期记忆
    4. 支持知识检索增强（RAG）
    """
    
    def __init__(self, memory_manager: MemoryManager, short_term_memory: ShortTermMemory):
        """
        初始化上下文工程师
        
        Args:
            memory_manager: 长期记忆管理器
            short_term_memory: 短期记忆管理器
        """
        self.memory_manager = memory_manager
        self.short_term_memory = short_term_memory
    
    def build_system_prompt(self, base_prompt: str, include_user_context: bool = True) -> str:
        """
        动态构建系统提示
        
        Args:
            base_prompt: 基础系统提示
            include_user_context: 是否包含用户上下文
            
        Returns:
            完整的系统提示
        """
        prompt_parts = [base_prompt]
        
        # 添加用户上下文
        if include_user_context:
            user_context = self.memory_manager.get_user_context()
            if user_context:
                prompt_parts.append(f"\n## 用户信息\n{user_context}")
        
        # 添加相关知识（可选）
        # 这里可以根据当前对话主题检索知识库
        
        return "\n".join(prompt_parts)
    
    def build_messages_with_context(
        self, 
        system_prompt: str,
        include_knowledge: bool = False,
        knowledge_query: Optional[str] = None
    ) -> List[Dict]:
        """
        构建包含完整上下文的消息列表
        
        Args:
            system_prompt: 系统提示
            include_knowledge: 是否包含知识库检索
            knowledge_query: 知识检索查询
            
        Returns:
            完整的消息列表
        """
        messages = []
        
        # 1. 系统消息（带用户上下文）
        full_system_prompt = self.build_system_prompt(system_prompt)
        
        # 2. 如果需要，添加检索到的知识
        if include_knowledge and knowledge_query:
            knowledge_results = self.memory_manager.search_knowledge(knowledge_query)
            if knowledge_results:
                knowledge_text = "\n".join([f"- {k}" for k in knowledge_results])
                full_system_prompt += f"\n\n## 相关知识\n{knowledge_text}"
        
        messages.append({
            "role": "system",
            "content": full_system_prompt
        })
        
        # 3. 添加短期记忆中的对话历史（排除系统消息）
        for msg in self.short_term_memory.get_messages():
            if msg.get("role") != "system":
                messages.append(msg)
        
        return messages
    
    def should_save_to_long_term(self, user_message: str, assistant_response: str) -> Dict[str, Any]:
        """
        判断是否应该保存到长期记忆
        
        判断规则：
        - 偏好类：包含"我喜欢"、"我偏好"等关键词
        - 事实类：包含"我叫"、"我是"等个人信息
        - 知识类：长文本且包含专业术语（如"AFM"、"寄存器"）
        
        Args:
            user_message: 用户消息
            assistant_response: 助手回复
            
        Returns:
            包含判断结果和元数据的字典
        """
        save_decision = {
            "should_save": False,
            "save_type": None,  # "preference" | "fact" | "knowledge"
            "content": None
        }
        
        user_lower = user_message.lower()
        
        # 规则1: 用户明确表达偏好
        preference_keywords = ["我喜欢", "我偏好", "我倾向于", "我想", "记住", "下次"]
        if any(kw in user_lower for kw in preference_keywords):
            save_decision["should_save"] = True
            save_decision["save_type"] = "preference"
            save_decision["content"] = user_message
        
        # 规则2: 用户提供个人信息
        personal_keywords = ["我叫", "我是", "我的名字", "我在", "我住在"]
        if any(kw in user_lower for kw in personal_keywords):
            save_decision["should_save"] = True
            save_decision["save_type"] = "fact"
            save_decision["content"] = user_message
        
        # 规则3: 重要的知识或事实（长度较长且包含专业术语）
        if len(user_message) > 100 and ("AFM" in user_message or "寄存器" in user_message):
            save_decision["should_save"] = True
            save_decision["save_type"] = "knowledge"
            save_decision["content"] = f"Q: {user_message[:100]}... A: {assistant_response[:100]}..."
        
        return save_decision
    
    def process_save_decision(self, decision: Dict[str, Any]):
        """处理保存决策"""
        if not decision["should_save"]:
            return
        
        content = decision["content"]
        save_type = decision["save_type"]
        
        if save_type == "preference":
            # 提取偏好信息（简化：直接存储）
            self.memory_manager.update_user_profile("preferences", {
                "latest_preference": content,
                "timestamp": datetime.now().isoformat()
            })
        elif save_type == "fact":
            self.memory_manager.update_user_profile("important_facts", content)
        elif save_type == "knowledge":
            self.memory_manager.add_knowledge(content, category="conversation")


def create_context_system(memory_dir: str = "memory") -> tuple:
    """
    创建完整的上下文工程系统（工厂函数）
    
    用法示例：
        memory_mgr, short_mem, ctx_eng = create_context_system("my_memory")
    
    Returns:
        (memory_manager, short_term_memory, context_engineer)
    """
    memory_manager = MemoryManager(memory_dir)
    short_term_memory = ShortTermMemory(max_messages=20, max_tokens=4000)
    context_engineer = ContextEngineer(memory_manager, short_term_memory)
    
    return memory_manager, short_term_memory, context_engineer
