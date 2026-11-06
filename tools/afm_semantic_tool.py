import os
import json
from typing import List, Dict, Any, Optional
import requests


class AFMSemanticTool:
    """
    AFM 语义检索工具：对 AFM 常见问题进行语义搜索（embedding/rerank）。
    依赖 Context/AFM扫描常见问题及解决.md 作为数据源。

    环境变量：
    - SILICONFLOW_API_KEY（优先使用），也可从参数传入 api_key
    """

    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.context_dir = os.path.join(self.project_root, 'Context')
        self.faq_path = os.path.join(self.context_dir, 'AFM扫描常见问题及解决.md')

    # ------------------------- Public: LLM Tool Definition -------------------------
    def get_tool_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_afm_issue_semantic",
                    "description": "对 AFM 常见问题进行语义检索，支持 rerank 或 embedding 相似度。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "查询问题或关键词（中文）"},
                            "category": {"type": "string", "description": "类别过滤：故障|曲线测试|扫描", "enum": ["故障", "曲线测试", "扫描"]},
                            "top_k": {"type": "integer", "description": "返回条目数", "default": 3},
                            "use": {"type": "string", "description": "使用后端：rerank 或 embedding", "enum": ["rerank", "embedding"], "default": "rerank"},
                            "model": {"type": "string", "description": "后端模型名（可选，默认使用 Qwen 系列）"},
                            "api_key": {"type": "string", "description": "SiliconFlow API Key（可选，若不提供则读环境变量）"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    # ------------------------- Public: Handlers -------------------------
    def handle_search_afm_issue_semantic(self, query: str, category: Optional[str] = None,
                                         top_k: int = 3, use: str = 'rerank',
                                         model: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        items = self._load_faq_items()
        if category:
            items = [it for it in items if it.get('category') == category]
        if not items:
            return {"results": [], "message": "未找到符合类别的数据。"}

        # 准备文档
        documents = [self._format_item_to_doc(it) for it in items]

        # 选择后端
        api_key = api_key or os.environ.get('SILICONFLOW_API_KEY')
        if not api_key:
            return {"error": "缺少 SiliconFlow API Key。请传入 api_key 或设置环境变量 SILICONFLOW_API_KEY。"}

        if use == 'embedding':
            model = model or 'Qwen/Qwen3-Embedding-8B'
            scores = self._embedding_scores(api_key, model, query, documents)
            ranked = sorted(zip(range(len(documents)), scores), key=lambda x: x[1], reverse=True)[:top_k]
        else:
            model = model or 'Qwen/Qwen3-Reranker-8B'
            ranks = self._rerank(api_key, model, query, documents)
            ranked = [(r['index'], r.get('relevance_score', r.get('score', 0))) for r in ranks[:top_k]]

        # 组装返回
        results = []
        for idx, score in ranked:
            item = items[idx]
            results.append({
                "id": item.get("id"),
                "category": item.get("category"),
                "question": item.get("question"),
                "cause": item.get("cause"),
                "solution": item.get("solution"),
                "score": score
            })
        return {"results": results, "count": len(results), "backend": use, "model": model}

    # ------------------------- Private: SiliconFlow Calls -------------------------
    def _rerank(self, api_key: str, model: str, query: str, documents: List[str]) -> List[Dict[str, Any]]:
        url = "https://api.siliconflow.cn/v1/rerank"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        payload = {"model": model, "query": query, "documents": documents}
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # 兼容不同返回格式
        if isinstance(data, dict) and 'results' in data:
            return data['results']
        if isinstance(data, list):
            return data
        return []

    def _embedding_scores(self, api_key: str, model: str, query: str, documents: List[str]) -> List[float]:
        url = "https://api.siliconflow.cn/v1/embeddings"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        # 获取 query embedding
        q_resp = requests.post(url, json={"model": model, "input": query}, headers=headers, timeout=30)
        q_resp.raise_for_status()
        q_vec = self._extract_embedding(q_resp.json())

        # 获取 docs embedding
        d_resp = requests.post(url, json={"model": model, "input": documents}, headers=headers, timeout=60)
        d_resp.raise_for_status()
        d_vecs = self._extract_embeddings(d_resp.json())

        # 计算 cosine 相似度
        def cosine(a: List[float], b: List[float]) -> float:
            import math
            dot = sum(x*y for x, y in zip(a, b))
            na = math.sqrt(sum(x*x for x in a))
            nb = math.sqrt(sum(x*x for x in b))
            return dot / (na*nb + 1e-12)

        return [cosine(q_vec, dv) for dv in d_vecs]

    def _extract_embedding(self, data: Any) -> List[float]:
        # 兼容 SiliconFlow embeddings 返回结构
        if isinstance(data, dict) and 'data' in data and data['data']:
            return data['data'][0].get('embedding', [])
        return []

    def _extract_embeddings(self, data: Any) -> List[List[float]]:
        if isinstance(data, dict) and 'data' in data:
            return [e.get('embedding', []) for e in data['data']]
        return []

    # ------------------------- Private: Data Preparation -------------------------
    def _load_faq_items(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.faq_path):
            return []
        with open(self.faq_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self._parse_faq_markdown(content)

    def _parse_faq_markdown(self, content: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        category: Optional[str] = None
        in_table = False
        headers: List[str] = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            # 类别标题
            if line.startswith('#'):
                # 提取末级标题作为类别名
                category = line.replace('#', '').strip()
                continue
            # 表头与分隔线
            if line.startswith('|'):
                cells = [c.strip() for c in line.strip('|').split('|')]
                if set(cells) == set(['---']) or all(set(c) <= set('-:') for c in cells):
                    # 分隔线
                    in_table = True
                    continue
                if not headers:
                    headers = cells
                    continue
                # 数据行
                row = cells
                if len(row) != len(headers):
                    continue
                data = dict(zip(headers, row))
                item = {
                    'category': category,
                    'id': self._safe_int(data.get('序号') or data.get('编号') or data.get('ID')),
                    'question': data.get('问题') or data.get('故障现象') or data.get('描述'),
                    'cause': data.get('可能原因') or data.get('原因') or data.get('分析'),
                    'solution': data.get('解决办法') or data.get('解决方案') or data.get('处理')
                }
                items.append(item)
        return items

    def _safe_int(self, x: Any) -> Optional[int]:
        try:
            return int(str(x).strip())
        except Exception:
            return None

    def _format_item_to_doc(self, item: Dict[str, Any]) -> str:
        return (
            f"[{item.get('category')}] 序号: {item.get('id')}\n"
            f"问题: {item.get('question')}\n"
            f"可能原因: {item.get('cause')}\n"
            f"解决办法: {item.get('solution')}"
        )