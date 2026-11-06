"""
AFM 工具
基于 Context 目录下的资料文件，提供以下功能：
1) 获取 AFM 助手提示词
2) 查询 AFM 扫描常见问题及解决方案
3) 校验 AFM 寄存器配置指令是否符合通讯协议 V37
4) 检索通讯协议 V37 中的寄存器信息
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from mcp.types import TextContent


class AFMTool:
    """AFM 相关工具集合"""

    def __init__(self):
        # 定位 Context 目录
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.context_dir = os.path.join(base_dir, "Context")
        self.prompt_path = os.path.join(self.context_dir, "AFM助手提示词.md")
        self.faq_path = os.path.join(self.context_dir, "AFM扫描常见问题及解决.md")
        self.protocol_path = os.path.join(self.context_dir, "通讯协议V37.py")

    # ------------------------------
    # 工具定义（用于 LLM tools 参数）
    # ------------------------------
    def get_tool_definition(self) -> List[Dict[str, Any]]:
        """返回多个工具函数定义，供 LLM tools 使用"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_afm_prompt",
                    "description": "读取并返回 AFM 助手提示词全文",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_afm_issue",
                    "description": "查询 AFM 扫描常见问题，按类别或编号或问题关键词返回成因和解决方案",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "问题类别：故障|曲线测试|扫描（可选）"
                            },
                            "id": {
                                "type": "integer",
                                "description": "问题编号（可选）"
                            },
                            "question": {
                                "type": "string",
                                "description": "问题关键词或描述（可选）"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "返回匹配条目数量（默认1）",
                                "default": 1
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_afm_registers",
                    "description": "校验寄存器配置指令列表是否符合通讯协议 V37 的类型、范围和步进要求",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "commands": {
                                "type": "array",
                                "description": "寄存器配置指令列表，每项包含 reg 地址和 value",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "reg": {"type": "string", "description": "寄存器地址（如 '00060001'）"},
                                        "value": {"type": "number", "description": "设置的值（switch 类型也使用数字 0/1）"}
                                    },
                                    "required": ["reg", "value"]
                                }
                            }
                        },
                        "required": ["commands"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_protocol_register",
                    "description": "检索通讯协议 V37 的寄存器信息，支持按地址或名称关键词查询",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "查询关键词：寄存器地址（如 00060001 或 REG61）或名称/描述关键词"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    # ------------------------------
    # 工具处理函数（用于 MCP server 调用）
    # ------------------------------
    def handle_get_afm_prompt(self, _arguments: Dict[str, Any]) -> List[TextContent]:
        """返回 AFM 助手提示词全文"""
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(type="text", text=f"读取提示词失败：{e}")]

    def handle_query_afm_issue(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """查询 AFM 扫描常见问题"""
        try:
            tables = self._parse_issue_tables()
            category = arguments.get("category")
            issue_id = arguments.get("id")
            question = arguments.get("question")
            top_k = int(arguments.get("top_k", 1) or 1)

            candidates: List[Dict[str, Any]] = []

            # 选择类别
            categories_order = ["故障", "曲线测试", "扫描"]
            if category:
                category_key = self._normalize_category(category)
                items = tables.get(category_key, [])
            else:
                # 合并所有类别
                items = []
                for cat in categories_order:
                    items.extend(tables.get(cat, []))

            # 复杂字符匹配迁移至 AFMSemanticTool
            if question and issue_id is None:
                msg = (
                    "该工具不再执行复杂字符匹配，请改用 'search_afm_issue_semantic' 进行语义检索（支持 embedding/rerank）。"
                    "可保留 category 作为过滤条件。"
                )
                return [TextContent(type="text", text=msg)]

            # 按编号筛选
            if issue_id is not None:
                for it in items:
                    try:
                        if int(it.get("编号", -1)) == int(issue_id):
                            candidates.append(it)
                    except Exception:
                        pass

            # 如果没有任何筛选参数，默认返回该类别（或全部）的前 top_k 条
            if not candidates:
                candidates = items[:top_k]

            if not candidates:
                return [TextContent(type="text", text="未找到匹配的问题条目。")]

            # 格式化输出
            parts: List[str] = []
            for it in candidates:
                parts.append(
                    (
                        f"【编号】{it.get('编号','')}\n"
                        f"【问题】{it.get('问题','')}\n"
                        f"【可能原因】{it.get('可能原因','')}\n"
                        f"【解决办法】{it.get('解决办法','')}\n"
                    ).strip()
                )
            return [TextContent(type="text", text="\n\n".join(parts))]
        except Exception as e:
            return [TextContent(type="text", text=f"查询失败：{e}")]

    def handle_validate_afm_registers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """校验寄存器配置指令列表"""
        try:
            commands = arguments.get("commands")
            if not isinstance(commands, list) or not commands:
                return [TextContent(type="text", text="参数错误：请提供非空的 commands 列表")]

            protocol = self._load_protocol()
            if not protocol:
                return [TextContent(type="text", text="协议加载失败：未找到 AFM_protocol_V37")]

            regs = protocol.get("registers", {})
            # 建立 address -> meta 的映射
            by_addr: Dict[str, Dict[str, Any]] = {}
            for meta in regs.values():
                addr = str(meta.get("address", "")).strip()
                if addr:
                    by_addr[addr] = meta

            results: List[Dict[str, Any]] = []
            all_ok = True

            for cmd in commands:
                reg_addr = str(cmd.get("reg", "")).strip()
                value = cmd.get("value")

                entry = by_addr.get(reg_addr)
                if not entry:
                    results.append({
                        "reg": reg_addr,
                        "status": "error",
                        "message": "寄存器地址不存在于协议"
                    })
                    all_ok = False
                    continue

                rtype = entry.get("type")
                status = "ok"
                message = "校验通过"

                # 类型与范围校验
                if rtype == "switch":
                    allowed = entry.get("options") or {}
                    allowed_keys = set()
                    # options 键可能是字符串数字
                    for k in allowed.keys():
                        try:
                            allowed_keys.add(int(k))
                        except Exception:
                            pass
                    if isinstance(value, (int, float)):
                        ivalue = int(value)
                        if ivalue not in allowed_keys:
                            status = "error"
                            message = f"值 {value} 不在允许选项 {sorted(list(allowed_keys))} 内"
                    else:
                        status = "error"
                        message = "switch 类型值需为数字 0/1 等"

                elif rtype == "parameter":
                    rng = entry.get("range")
                    step = entry.get("step")
                    if rng and isinstance(rng, list) and len(rng) == 2:
                        lo, hi = float(rng[0]), float(rng[1])
                        try:
                            fval = float(value)
                            if fval < lo or fval > hi:
                                status = "error"
                                message = f"值 {fval} 超出范围 [{lo}, {hi}]"
                            elif step is not None:
                                try:
                                    fstep = float(step)
                                    # 允许一定的浮点误差
                                    if fstep > 0:
                                        # 与默认值的整步关系不强制；仅校验步进粒度
                                        remainder = abs((fval - float(entry.get("default", 0))) % fstep)
                                        tol = max(1e-9, fstep / 10000)
                                        if remainder > tol and abs(remainder - fstep) > tol:
                                            status = "error"
                                            message = f"值 {fval} 与步进 {fstep} 不对齐"
                                except Exception:
                                    pass
                        except Exception:
                            status = "error"
                            message = "parameter 类型值需为数字"
                    else:
                        # 无范围信息，则仅检查数值类型
                        try:
                            _ = float(value)
                        except Exception:
                            status = "error"
                            message = "parameter 类型值需为数字"
                else:
                    # 未知类型，跳过严格校验
                    message = f"未知类型 {rtype}，跳过严格校验"

                if status != "ok":
                    all_ok = False

                results.append({
                    "reg": reg_addr,
                    "name": entry.get("name") or entry.get("name_zh"),
                    "type": rtype,
                    "status": status,
                    "message": message
                })

            summary = {
                "overall": "ok" if all_ok else "error",
                "count": len(results)
            }

            text = ["AFM 寄存器配置校验结果：", json.dumps(summary, ensure_ascii=False, indent=2), "明细："]
            for r in results:
                text.append(json.dumps(r, ensure_ascii=False))

            return [TextContent(type="text", text="\n".join(text))]
        except Exception as e:
            return [TextContent(type="text", text=f"校验失败：{e}")]

    def handle_search_protocol_register(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """检索协议中的寄存器信息"""
        try:
            query = str(arguments.get("query", "")).strip()
            if not query:
                return [TextContent(type="text", text="参数错误：query 不能为空")]

            protocol = self._load_protocol()
            if not protocol:
                return [TextContent(type="text", text="协议加载失败：未找到 AFM_protocol_V37")]

            regs = protocol.get("registers", {})
            q_lower = query.lower()

            results: List[Dict[str, Any]] = []

            # 支持地址直接匹配（包含 REGxx 或 16进制地址）
            for key, meta in regs.items():
                addr = str(meta.get("address", ""))
                name = (meta.get("name") or meta.get("name_zh") or "")
                desc = str(meta.get("description", ""))

                hit = False
                if query.upper().startswith("REG") and key.upper() == query.upper():
                    hit = True
                elif re.fullmatch(r"[0-9A-Fa-f]{8}", query) and addr.lower() == query.lower():
                    hit = True
                elif q_lower in addr.lower() or q_lower in name.lower() or q_lower in desc.lower():
                    hit = True

                if hit:
                    results.append({
                        "reg": key,
                        "address": addr,
                        "name": name,
                        "type": meta.get("type"),
                        "range": meta.get("range"),
                        "default": meta.get("default"),
                        "options": meta.get("options"),
                        "description": desc
                    })

            if not results:
                return [TextContent(type="text", text="未找到匹配的寄存器信息")]

            text_lines = ["查询结果（可能多项）："]
            for r in results[:10]:  # 限制最多返回10条，避免过长
                text_lines.append(json.dumps(r, ensure_ascii=False))
            return [TextContent(type="text", text="\n".join(text_lines))]
        except Exception as e:
            return [TextContent(type="text", text=f"查询失败：{e}")]

    # ------------------------------
    # 辅助方法
    # ------------------------------
    def _normalize_category(self, c: str) -> str:
        c = c.strip()
        if c.startswith("故障"):
            return "故障"
        if c.startswith("曲线"):
            return "曲线测试"
        if c.startswith("扫描"):
            return "扫描"
        return c

    def _simple_match_score(self, text: str, q: str) -> float:
        """简单匹配评分：包含给 1.0；否则根据重叠比例估计"""
        t = text.lower()
        ql = q.lower()
        if ql in t:
            return 1.0
        # 粗略字符重叠比
        overlap = sum(1 for ch in set(ql) if ch in t)
        return overlap / max(1, len(set(ql)))

    def _parse_issue_tables(self) -> Dict[str, List[Dict[str, str]]]:
        """解析 AFM扫描常见问题及解决.md 中的三个表格，返回 {类别: [条目...]}"""
        with open(self.faq_path, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f]

        out: Dict[str, List[Dict[str, str]]] = {"故障": [], "曲线测试": [], "扫描": []}
        current_cat: Optional[str] = None
        in_table = False
        header_cols: List[str] = []

        def add_row(cat: str, cols: List[str]):
            if len(cols) < 4:
                return
            item = {header_cols[0]: cols[0], header_cols[1]: cols[1], header_cols[2]: cols[2], header_cols[3]: cols[3]}
            out.setdefault(cat, []).append(item)

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 识别类别标题
            if line.endswith("类："):
                if line.startswith("故障"):
                    current_cat = "故障"
                elif line.startswith("曲线测试"):
                    current_cat = "曲线测试"
                elif line.startswith("扫描"):
                    current_cat = "扫描"
                else:
                    current_cat = None
                in_table = False
                header_cols = []
                i += 1
                continue

            # 表头
            if current_cat and line.startswith("|") and not in_table and "编号" in line and "问题" in line:
                header_cols = [c.strip() for c in line.strip('|').split('|')]
                # 下一行可能是分隔线
                i += 1
                in_table = True
                # 跳过分隔线
                if i < len(lines) and lines[i].strip().startswith("|") and set(lines[i].replace(' ', '')) <= set("|-"):
                    i += 1
                continue

            # 表体行
            if current_cat and in_table and line.startswith("|"):
                cols = [c.strip() for c in line.strip('|').split('|')]
                # 只取前四列
                while len(cols) < 4:
                    cols.append("")
                add_row(current_cat, cols[:4])
                i += 1
                continue

            # 结束表格
            if in_table and (not line.startswith("|") or line == ""):
                in_table = False
                header_cols = []

            i += 1

        return out

    def _load_protocol(self) -> Dict[str, Any]:
        """加载 Context/通讯协议V37.py 中的 AFM_protocol_V37 字典"""
        with open(self.protocol_path, "r", encoding="utf-8") as f:
            src = f.read()

        # 在隔离命名空间执行，提取变量
        ns: Dict[str, Any] = {}
        exec(src, {}, ns)
        protocol = ns.get("AFM_protocol_V37")
        return protocol if isinstance(protocol, dict) else {}