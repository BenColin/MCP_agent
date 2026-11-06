"""
AFM 工具
基于 AFM_tool 目录的协议与文档，提供：
- 寄存器查询与详细信息
- 寄存器值校验
- 各工作模式标准控制流程（文本）
- 常见问题检索与解决建议
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from mcp.types import TextContent
import math
import requests

# 导入协议字典（包含全部寄存器定义）
from AFM_tool.通讯协议V37 import AFM_protocol_V37


class AFMTool:
    """AFM 相关工具集合"""

    def __init__(self) -> None:
        # 项目根目录：.../MCP_agent
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.docs_dir = os.path.join(self.project_root, "AFM_tool")
        # SiliconFlow API 配置
        self.sf_base = "https://api.siliconflow.cn/v1"
        self.embedding_model = "Qwen/Qwen3-Embedding-8B"
        self.rerank_model = "Qwen/Qwen3-Reranker-8B"

    # ----------------------
    # 工具定义（提供给LLM）
    # ----------------------
    def get_tool_definition(self) -> List[Dict[str, Any]]:
        """返回可供 LLM 使用的函数式工具定义集合"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "afm_list_registers",
                    "description": "列出AFM协议寄存器，支持按类型过滤与数量限制",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "寄存器类型过滤：parameter 或 switch",
                                "enum": ["parameter", "switch"]
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回的最大条目数，可选"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "afm_get_register_info",
                    "description": "查询指定寄存器的详细信息（支持代码或地址）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reg": {"type": "string", "description": "寄存器代码（如REG0B）或地址（如0000000B）"},
                            "by": {"type": "string", "enum": ["code", "address"], "description": "查询方式，默认为code"}
                        },
                        "required": ["reg"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "afm_validate_register_value",
                    "description": "校验寄存器写入值是否符合协议范围/步进/选项",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reg": {"type": "string", "description": "寄存器代码或地址"},
                            "value": {"type": "number", "description": "要写入的值（switch类型也可用数字表示选项）"},
                            "by": {"type": "string", "enum": ["code", "address"], "description": "查询方式，默认为code"}
                        },
                        "required": ["reg", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "afm_get_mode_standard_flow",
                    "description": "根据AFM助手文档返回指定模式的标准控制流程（纯文本说明）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "description": "工作模式：轻敲、接触、PFM、KPFM-AM、EFM、MFM",
                                "enum": ["轻敲", "接触", "PFM", "KPFM-AM", "EFM", "MFM"]
                            },
                            "include_notes": {
                                "type": "boolean",
                                "description": "是否附带注意事项说明，默认true",
                                "default": True
                            }
                        },
                        "required": ["mode"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "afm_search_troubleshooting",
                    "description": "按关键词检索AFM常见问题、可能原因与解决办法（支持分类过滤）",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "关键字，如‘共振峰’、‘扫描速度’等"},
                            "category": {"type": "string", "enum": ["故障类", "曲线测试类", "扫描类"], "description": "分类过滤，可选"},
                            "limit": {"type": "integer", "description": "最大返回条目数，默认5", "default": 5}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    # ----------------------
    # 具体实现（返回 TextContent）
    # ----------------------
    def handle_afm_list_registers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        reg_type = arguments.get("type")
        limit = arguments.get("limit")
        regs = AFM_protocol_V37.get("registers", {})

        entries: List[str] = []
        for code, meta in regs.items():
            if reg_type and meta.get("type") != reg_type:
                continue
            name = meta.get("name_zh") or meta.get("name") or code
            addr = meta.get("address")
            typ = meta.get("type")
            default = meta.get("default")
            entries.append(f"{code} | {addr} | {typ} | 默认: {default} | {name}")
            if isinstance(limit, int) and limit > 0 and len(entries) >= limit:
                break

        if not entries:
            return [TextContent(type="text", text="未找到符合条件的寄存器。")]

        header = "代码 | 地址 | 类型 | 默认值 | 名称"
        text = "\n".join([header] + entries)
        return [TextContent(type="text", text=text)]

    def handle_afm_get_register_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        reg = str(arguments.get("reg", "")).strip()
        by = str(arguments.get("by", "code")).strip() or "code"
        regs = AFM_protocol_V37.get("registers", {})

        meta = None
        if by == "code":
            meta = regs.get(reg)
        elif by == "address":
            # 线性搜索地址匹配
            for code, m in regs.items():
                if str(m.get("address")) == reg:
                    meta = {**m, "code": code}
                    break

        if not meta:
            return [TextContent(type="text", text=f"未找到寄存器：{reg}（by={by}）")]

        # 输出详细信息（JSON 格式）
        info = {
            "code": meta.get("code") or reg if by == "address" else reg,
            "address": meta.get("address"),
            "type": meta.get("type"),
            "name": meta.get("name_zh") or meta.get("name"),
            "description": meta.get("description"),
            "default": meta.get("default"),
            "range": meta.get("range"),
            "step": meta.get("step"),
            "options": meta.get("options")
        }
        return [TextContent(type="text", text=json.dumps(info, ensure_ascii=False, indent=2))]

    def handle_afm_validate_register_value(self, arguments: Dict[str, Any]) -> List[TextContent]:
        reg = str(arguments.get("reg", "")).strip()
        by = str(arguments.get("by", "code")).strip() or "code"
        value = arguments.get("value")

        regs = AFM_protocol_V37.get("registers", {})
        meta = None

        if by == "code":
            meta = regs.get(reg)
        elif by == "address":
            for code, m in regs.items():
                if str(m.get("address")) == reg:
                    meta = m
                    reg = code
                    break

        if not meta:
            return [TextContent(type="text", text=f"未找到寄存器：{reg}（by={by}）")]

        typ = meta.get("type")
        ok = True
        msg = "校验通过"

        try:
            if typ == "switch":
                options = meta.get("options", {})
                # 允许数字或字符串，统一转字符串比较
                v_str = str(int(value)) if isinstance(value, (int, float)) else str(value)
                if v_str not in options:
                    ok = False
                    msg = f"非法选项：{value}，允许值：{', '.join(options.keys())}"
            elif typ == "parameter":
                rng = meta.get("range") or [None, None]
                step = meta.get("step") or None
                try:
                    v = float(value)
                except Exception:
                    ok = False
                    msg = f"参数寄存器需要数值类型，收到：{value}"
                    v = None
                if v is not None and rng[0] is not None and rng[1] is not None:
                    if not (rng[0] <= v <= rng[1]):
                        ok = False
                        msg = f"超出范围：{v} 不在 [{rng[0]}, {rng[1]}]"
                if ok and step:
                    # 以最小值为基准的步进校验（允许微小浮点误差）
                    base = rng[0] if rng[0] is not None else 0.0
                    ratio = (v - base) / float(step)
                    # 判断接近整数
                    if abs(round(ratio) - ratio) > 1e-9:
                        ok = False
                        msg = f"与步进不匹配：{v} 相对于基准 {base} 的步进应为 {step} 的整数倍"
            else:
                msg = f"未知寄存器类型：{typ}"
                ok = False
        except Exception as e:
            ok = False
            msg = f"校验异常：{str(e)}"

        result = {
            "code": reg,
            "type": typ,
            "value": value,
            "valid": ok,
            "message": msg
        }
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    def handle_afm_get_mode_standard_flow(self, arguments: Dict[str, Any]) -> List[TextContent]:
        mode = str(arguments.get("mode", "")).strip()
        include_notes = bool(arguments.get("include_notes", True))

        flows = self._parse_standard_flows()
        if mode not in flows:
            return [TextContent(type="text", text=f"不支持的模式：{mode}。支持：{', '.join(flows.keys())}")]

        text_parts = [f"📋 模式：{mode}", f"流程：{flows[mode]}"]
        if include_notes and flows.get("notes"):
            text_parts.append("\n⚠️ 注意事项：")
            for note in flows["notes"]:
                text_parts.append(f"- {note}")

        return [TextContent(type="text", text="\n".join(text_parts))]

    def handle_afm_search_troubleshooting(self, arguments: Dict[str, Any]) -> List[TextContent]:
        query = str(arguments.get("query", "")).strip()
        category = arguments.get("category")
        limit = int(arguments.get("limit", 5))

        tables = {
            "故障类": self._parse_troubles_table("故障类："),
            "曲线测试类": self._parse_troubles_table("曲线测试类："),
            "扫描类": self._parse_troubles_table("扫描类：")
        }

        # 聚合候选条目
        candidates: List[Dict[str, str]] = []
        if category and category in tables:
            for e in tables[category]:
                e["_category"] = category
                candidates.append(e)
        else:
            for cat_name, cat in tables.items():
                for e in cat:
                    e["_category"] = cat_name
                    candidates.append(e)

        if not candidates:
            return [TextContent(type="text", text="未解析到任何常见问题表格。")]

        # 构造文档字符串
        docs: List[str] = []
        index_map: Dict[str, int] = {}
        for idx, item in enumerate(candidates):
            doc = f"[{item.get('_category','')}] 编号{item.get('编号','')} | 问题：{item.get('问题','')} | 可能原因：{item.get('可能原因','')} | 解决办法：{item.get('解决办法','')}"
            docs.append(doc)
            index_map[doc] = idx

        # 若存在 API Key，执行 embedding + rerank；否则退化为关键词匹配
        api_key = os.environ.get("SILICONFLOW_API_KEY")
        if api_key and query:
            try:
                # 1) Embedding：计算 query 与每个 doc 的余弦相似度，筛选 topM
                q_vec = self._sf_embed(query, api_key)
                sims = []
                for i, doc in enumerate(docs):
                    d_vec = self._sf_embed(doc, api_key)
                    sims.append((i, self._cosine(q_vec, d_vec)))
                sims.sort(key=lambda x: x[1], reverse=True)
                top_m = [docs[i] for i, _ in sims[:max(limit * 4, 10)]]

                # 2) Rerank：对 topM 文档进行重排
                reranked = self._sf_rerank(query, top_m, api_key)
                ordered_docs = [r["document"] for r in reranked]

                # 3) 格式化输出
                lines: List[str] = [f"🔎 关键词：{query}"]
                if category:
                    lines.append(f"📂 分类：{category}")
                lines.append("")

                for i, doc in enumerate(ordered_docs[:limit], start=1):
                    item = candidates[index_map[doc]]
                    lines.append(f"#{i} 编号：{item.get('编号')}")
                    lines.append(f"问题：{item.get('问题')}")
                    lines.append(f"可能原因：{item.get('可能原因')}")
                    lines.append(f"解决办法：{item.get('解决办法')}\n")

                return [TextContent(type="text", text="\n".join(lines).strip())]
            except Exception as e:
                # 失败则回退到关键词匹配
                fallback = self._keyword_search_format(query, category, candidates, limit)
                fallback_text = f"⚠️ ML检索失败，使用关键词匹配。原因：{str(e)}\n\n" + fallback
                return [TextContent(type="text", text=fallback_text)]
        else:
            # 无 API Key 或空查询：纯关键词匹配
            return [TextContent(type="text", text=self._keyword_search_format(query, category, candidates, limit))]

    # ----------------------
    # 文档/协议解析辅助
    # ----------------------
    def _parse_standard_flows(self) -> Dict[str, Any]:
        """从 AFM助手提示词.md 提取各模式的标准流程与注意事项"""
        path = os.path.join(self.docs_dir, "AFM助手提示词.md")
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            return {}

        flows: Dict[str, str] = {}
        # 逐行查找流程条目
        lines = [l.strip() for l in text.splitlines()]
        patterns = {
            "轻敲": re.compile(r"^1\.?\s*AFM（轻敲模式）[:：](.+)$"),
            "接触": re.compile(r"^2\.?\s*AFM（接触模式）[:：](.+)$"),
            "PFM": re.compile(r"^3\.?\s*PFM[:：](.+)$"),
            "KPFM-AM": re.compile(r"^4\.?\s*KPFM-AM[:：](.+)$"),
            "EFM": re.compile(r"^5\.?\s*EFM[:：](.+)$"),
            "MFM": re.compile(r"^6\.?\s*MFM[:：](.+)$"),
        }

        for line in lines:
            for key, pat in patterns.items():
                m = pat.match(line)
                if m:
                    flows[key] = m.group(1).strip()

        # 提取注意事项（紧随“以下3点尤为重要”段落下的三条）
        notes: List[str] = []
        gathering = False
        for line in lines:
            if "以下3点尤为重要" in line:
                gathering = True
                continue
            if gathering:
                if not line:
                    # 空行视为段落结束
                    if notes:
                        break
                    else:
                        continue
                # 去掉可能的序号与顿号
                cleaned = re.sub(r"^[\d、。，：:]+", "", line)
                notes.append(cleaned)

        flows["notes"] = notes
        return flows

    def _parse_troubles_table(self, section_title: str) -> List[Dict[str, str]]:
        """从 AFM扫描常见问题及解决.md 中解析指定段落的表格为字典列表"""
        path = os.path.join(self.docs_dir, "AFM扫描常见问题及解决.md")
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            return []

        # 找到段落起始
        start_idx = text.find(section_title)
        if start_idx == -1:
            return []
        # 从起始到文件末尾或下一个段落
        chunk = text[start_idx:]

        # 提取表格行（以 | 分隔的行）
        rows = [ln.strip() for ln in chunk.splitlines() if ln.strip().startswith("|")]
        if len(rows) < 3:
            return []

        headers = [h.strip() for h in rows[0].strip("|").split("|")]
        data_rows = rows[2:]  # 跳过分隔行
        items: List[Dict[str, str]] = []
        for r in data_rows:
            cols = [c.strip() for c in r.strip("|").split("|")]
            if len(cols) != len(headers):
                # 可能不是完整行，跳过
                continue
            entry = {headers[i]: cols[i] for i in range(len(headers))}
            items.append(entry)
        return items

    # ----------------------
    # SiliconFlow API helpers
    # ----------------------
    def _sf_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }

    def _sf_embed(self, text: str, api_key: str) -> List[float]:
        url = f"{self.sf_base}/embeddings"
        payload = {
            "model": self.embedding_model,
            "input": text
        }
        resp = requests.post(url, json=payload, headers=self._sf_headers(api_key), timeout=30)
        data = resp.json()
        if resp.status_code != 200:
            raise Exception(data.get("error", {}).get("message", f"HTTP {resp.status_code}"))
        # 通常返回结构包含 data[0].embedding
        emb = None
        if isinstance(data, dict) and "data" in data and data["data"]:
            emb = data["data"][0].get("embedding")
        elif "embedding" in data:
            emb = data.get("embedding")
        if not emb:
            raise Exception("未获取到embedding向量")
        return emb

    def _sf_rerank(self, query: str, documents: List[str], api_key: str) -> List[Dict[str, Any]]:
        url = f"{self.sf_base}/rerank"
        payload = {
            "model": self.rerank_model,
            "query": query,
            "documents": documents
        }
        resp = requests.post(url, json=payload, headers=self._sf_headers(api_key), timeout=30)
        data = resp.json()
        if resp.status_code != 200:
            raise Exception(data.get("error", {}).get("message", f"HTTP {resp.status_code}"))
        # 期待 results 列表包含重排后的文档与分数
        results = data.get("results") or []
        # 规范化输出 {document, score}
        ordered = []
        for r in results:
            doc = r.get("document") if isinstance(r.get("document"), str) else None
            score = r.get("relevance_score") or r.get("score")
            if doc:
                ordered.append({"document": doc, "score": score})
        # 若返回未包含原文档（有些API返回索引），尝试按index映射
        if not ordered and all(isinstance(r.get("index"), int) for r in results):
            for r in results:
                idx = r.get("index")
                score = r.get("relevance_score") or r.get("score")
                if 0 <= idx < len(documents):
                    ordered.append({"document": documents[idx], "score": score})
        if not ordered:
            # 如果返回结构不可识别，则直接返回传入的文档
            ordered = [{"document": d, "score": None} for d in documents]
        return ordered

    def _cosine(self, v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a*b for a,b in zip(v1,v2))
        n1 = math.sqrt(sum(a*a for a in v1))
        n2 = math.sqrt(sum(b*b for b in v2))
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1*n2)

    def _keyword_search_format(self, query: str, category: Optional[str], candidates: List[Dict[str, str]], limit: int) -> str:
        def match(entry: Dict[str, str]) -> bool:
            text = (entry.get("问题", "") + " " + entry.get("可能原因", "") + " " + entry.get("解决办法", "")).lower()
            return query.lower() in text if query else True
        results = [e for e in candidates if match(e)]
        if not results:
            return f"未检索到与“{query}”相关的条目。"
        lines: List[str] = [f"🔎 关键词：{query}"]
        if category:
            lines.append(f"📂 分类：{category}")
        lines.append("")
        for i, item in enumerate(results[:limit], start=1):
            lines.append(f"#{i} 编号：{item.get('编号')}")
            lines.append(f"问题：{item.get('问题')}")
            lines.append(f"可能原因：{item.get('可能原因')}")
            lines.append(f"解决办法：{item.get('解决办法')}\n")
        return "\n".join(lines).strip()