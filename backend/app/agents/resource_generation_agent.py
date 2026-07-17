"""
资源生成智能体

根据学习路径和资源类型生成具体的个性化学习资源。
支持证据优先生成：生成前检索教材原文作为上下文，生成后校验引用一致性。
"""
import logging
import re
import uuid
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_RESOURCE_GENERATION = """你是一个专业的教育资源生成智能体。请根据以下信息，为学生生成个性化学习资源。

## 学习路径
{learning_path}

## 资源类型：{resource_type}
## 难度：{difficulty}
## 学生信息：{student_info}

## 本次生成约束
{generation_requirements}

## 教材原文依据（务必引用，chunk_id 格式为数字）
{evidence_context}

## 生成要求
1. **必须引用教材原文**：在关键概念、定义、结论处加 [引用:chunk_id]，chunk_id 来自上述依据
2. **不得随意延伸**：生成内容应与上述原文保持一致，有争议处标注 [草稿:缺乏充分教材依据]
3. 知识讲解清晰准确，有具体示例
4. 练习题有答案和简要解析
5. 代码示例必须可直接运行，附运行说明
6. 适合难度：{difficulty}

{type_specific_instruction}

## 输出要求
- 直接输出 Markdown 格式学习资源内容
- 总字数控制在 1500 字以内（不含代码）
- 结构清晰，含小标题分层
"""

PROMPT_HALLUCINATION_CHECK = """你是一个严格的知识质量审查智能体。请对比以下「课程知识库」和「生成内容」，检查是否存在事实性错误或幻觉。

## 课程知识库（权威来源）
{context}

## 生成内容（待审查）
{content}

## 审查要求
请检查以下几类问题：
1. **事实性错误**：知识库中明确否定或与事实不符的陈述
2. **概念混淆**：将不同知识点的概念混用
3. **过时信息**：知识库有更新版本但生成内容仍用旧版本
4. **代码错误**：SQL/Python 代码与知识库描述的行为不一致
5. **超纲内容**：超出知识库范围且未标注"进阶内容"

请以 JSON 格式输出审查结果：
{{
  "has_hallucination": true/false,
  "warnings": [
    {{"type": "事实性错误", "location": "第2段第3句", "claim": "具体错误陈述", "correction": "正确陈述"}},
    ...
  ],
  "summary": "一句话总结"
}}

要求：
- has_hallucination: 存在任何事实性错误时为 true
- warnings: 列出所有发现的问题，无问题时为空数组 []
- 每条 warning 需包含 type/location/claim/correction
- 只输出 JSON，不要有其他内容
"""


INSTRUCTION_MAP = {
    "lecture": """## 资源类型要求（讲义）
生成一份知识点讲义，包含：
- 概述：简述本知识点的重要性
- 核心概念：定义和原理
- 详细讲解：分层次展开
- 代码示例：SQL / Python / 其他语言示例
- 常见错误和注意事项
- 练习题（3-5道）+ 答案解析""",

    "quiz": """## 资源类型要求（习题）
生成一套练习题，包含：
- 选择题（5道）+ 答案
- 简答题（2道）+ 参考答案
- 编程题（1道）+ 参考答案
- 每道题有知识点标注""",

    "ppt": """## 资源类型要求（PPT大纲）
生成 PPT 大纲，包含：
- 封面标题
- 每页标题 + 要点（6-10页）
- 每页备注区内容""",

    "case": """## 资源类型要求（案例材料）
生成一个教学案例，包含：
- 案例背景
- 问题描述
- 分析思路
- 解决方案
- 案例思考题""",

    "review": """## 资源类型要求（复习计划）
生成复习计划，包含：
- 复习目标
- 每日任务安排（3-5天）
- 知识点回顾清单
- 自测题""",

    "test": """## 资源类型要求（阶段测验）
生成阶段测验，包含：
- 选择题（10道）+ 答案
- 判断题（5道）+ 答案
- 简答题（2道）+ 参考答案
- 测验说明（时间、满分、及格线）""",

    "mindmap": """## 资源类型要求（思维导图）
生成知识点的思维导图，以 Markdown 树形结构呈现，包含：
- 中心主题：知识点名称
- 一级分支：核心概念（3-5个）
- 二级分支：每个概念的关键要点
- 末级分支：具体示例或注意事项
- 整体结构层次分明，便于学生建立知识体系""",

    "code_case": """## 资源类型要求（代码实操案例）
生成一个完整的代码实操案例，包含：
- 案例目标：解决什么实际问题
- 需求描述：清晰的功能需求
- 代码实现：完整可运行的代码（Python/SQL/Java等）
- 运行结果：代码执行后的输出示例
- 关键讲解：代码中核心逻辑的解释
- 拓展练习：2-3道改编题""",

    "video_script": """## 资源类型要求（视频/动画脚本）
生成一个教学视频/动画脚本，包含：
- 视频标题和时长建议（3-5分钟）
- 分镜脚本：每段的文字内容、动画描述、时长
- 讲解旁白：配合每段画面的讲解词
- 视觉素材提示：需要展示的图表、代码、动画
- 互动问题：视频中设置的思考题""",

    "experiment_report": """## 资源类型要求（实验报告）
生成一份实验报告模板，包含：
- 实验目的：本次实验要掌握的知识点
- 实验环境：所需工具、环境配置
- 实验步骤：详细操作流程（分步骤）
- 预期结果：每个步骤的预期输出
- 结果分析：如何分析实验结果
- 常见问题与解决：实验中的典型问题
- 思考题：2-3道延伸思考""",

    "error_analysis": """## 资源类型要求（错题解析）
生成常见错误分析文档，包含：
- 错误类型分类（如：概念混淆、计算错误、审题失误）
- 每类错误的典型例题（含错误做法和正确做法）
- 错误原因剖析：为什么容易犯这个错
- 正确做法讲解：如何避免
- 配套练习：同类题目的变式练习""",

    "learning_card": """## 资源类型要求（学习卡片）
生成一组知识速记卡片（5-8张），每张卡片包含：
- 卡片标题：一个核心概念/公式/术语
- 正面：概念名称 + 简短定义
- 背面：详细解释 + 示例 + 记忆口诀
- 适合课间快速记忆和复习""",
}

RESOURCE_TYPE_TITLES = {
    "lecture": "知识点讲义",
    "ppt": "PPT大纲",
    "quiz": "习题与答案",
    "case": "案例材料",
    "review": "复习计划",
    "test": "阶段测验",
    "mindmap": "思维导图",
    "code_case": "代码实操案例",
    "video_script": "视频/动画脚本",
    "experiment_report": "实验报告",
    "error_analysis": "错题解析",
    "learning_card": "学习卡片",
}


class ResourceGenerationAgent:
    """资源生成智能体"""

    AGENT_NAME = "resource_generation_agent"
    AGENT_DESC = "资源生成智能体 — 生成个性化学习资源（证据优先）"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        learning_path: List[Dict[str, Any]],
        resource_type: str,
        difficulty: str,
        student_profile: Dict[str, Any],
        course_id: Optional[int] = None,
        generation_requirements: str = "无额外约束",
    ) -> Dict[str, Any]:
        """
        生成学习资源（证据优先链路）。

        Args:
            learning_path: 学习路径规划结果
            resource_type: 资源类型
            difficulty: 难度等级
            student_profile: 学生画像
            course_id: 课程 ID（用于证据检索）

        Returns:
            {
                "resource_id": str,
                "title": str,
                "type": str,
                "target_kp_ids": str,
                "knowledge_points": List[int],
                "difficulty": str,
                "content": str,
                "target_audience": str,
                "estimated_learning_time": str,
                "generation_metadata": dict,
                "hallucination_warnings": list,
                "trustworthiness": str,         # high/medium/low/draft
                "evidence_context": str,       # 注入的原文上下文（用于记录）
                "evidence_links": List[dict],   # 证据关联记录，待写入 DB
                "unfounded_kps": List[int],     # 缺乏教材依据的知识点 IDs
            }
        """
        logger.info(f"[{self.AGENT_NAME}] 生成资源: {resource_type}, course_id={course_id}")

        main_kp = learning_path[0] if learning_path else {}
        kp_name = main_kp.get("kp_name", "知识点")
        kp_ids = [p.get("kp_id", 0) for p in learning_path if p.get("kp_id")]
        kp_id_str = ",".join(str(kid) for kid in kp_ids) if kp_ids else ""

        path_text = "\n".join(
            f"{i+1}. [{p.get('kp_name', '')}] {p.get('resource_type', '')} | "
            f"预计 {p.get('estimated_time', '')} | 优先级: {p.get('priority', '')}"
            for i, p in enumerate(learning_path)
        ) or "（无学习路径数据）"

        student_info = (
            f"姓名：{student_profile.get('student_name', '未知')}，"
            f"学习目标：{student_profile.get('learning_goal', '暂无')}，"
            f"偏好资源类型：{', '.join(student_profile.get('resource_preferences', [])) or '暂无'}"
        )

        type_instruction = INSTRUCTION_MAP.get(resource_type, INSTRUCTION_MAP["lecture"])

        # === 证据检索（生成前）===
        evidence_result = self._retrieve_evidence(kp_ids, course_id, top_k=8)
        evidence_context = evidence_result["context_text"]
        evidence_chunks = evidence_result["evidence_chunks"]
        has_confirmed_knowledge = evidence_result["has_confirmed_knowledge"]

        # === LLM 生成（带证据上下文）===
        messages = [
            {
                "role": "user",
                "content": PROMPT_RESOURCE_GENERATION.format(
                    learning_path=path_text,
                    resource_type=RESOURCE_TYPE_TITLES.get(resource_type, "学习资源"),
                    difficulty=difficulty,
                    student_info=student_info,
                    generation_requirements=generation_requirements or "无额外约束",
                    evidence_context=evidence_context or "（当前课程暂无教材依据，请基于通用知识生成，并在关键结论处标注 [草稿:缺乏充分教材依据]）",
                    type_specific_instruction=type_instruction,
                )
            }
        ]

        content = self._call_llm(messages)

        if content is None:
            content = self._generate_content(kp_name, resource_type, difficulty, evidence_chunks)

        # === 引用一致性校验（生成后）===
        citation_result = self._verify_citations(content, evidence_chunks)
        trustworthiness = citation_result["trustworthiness"]
        valid_chunk_ids = citation_result["valid_chunk_ids"]
        unfounded_kps = citation_result["unfounded_kps"]

        # === 防幻觉检测 ===
        hallucination_warnings = []
        rag_context = self._retrieve_rag_for_check(kp_name, kp_ids, course_id)
        if rag_context and content and len(content) > 100:
            check_result = self._hallucination_check(content, rag_context)
            if check_result:
                hallucination_warnings = check_result.get("warnings", [])
                logger.info(f"[{self.AGENT_NAME}] 幻觉检测完成: {len(hallucination_warnings)} 个警告")

        # === 构建 evidence_links（供 workflow 写入 DB）===
        evidence_links = self._build_evidence_links(content, evidence_chunks, kp_ids)

        return {
            "resource_id": f"res-{uuid.uuid4().hex[:8]}",
            "title": f"{kp_name}专题{RESOURCE_TYPE_TITLES.get(resource_type, '资源')}",
            "type": resource_type,
            "type_label": RESOURCE_TYPE_TITLES.get(resource_type, "学习资源"),
            "target_kp_ids": kp_id_str,
            "knowledge_points": kp_ids,
            "difficulty": difficulty,
            "content": content,
            "target_audience": f"当前学习{difficulty}难度内容",
            "estimated_learning_time": f"约{30 + len(learning_path) * 10}分钟",
            "generation_metadata": {
                "agent": self.AGENT_NAME,
                "model": get_settings().llm_model,
            },
            "hallucination_warnings": hallucination_warnings,
            "trustworthiness": trustworthiness,
            "evidence_context": evidence_context,
            "evidence_links": evidence_links,
            "unfounded_kps": unfounded_kps,
        }

    def _retrieve_evidence(
        self,
        kp_ids: List[int],
        course_id: Optional[int],
        top_k: int = 8,
    ) -> Dict[str, Any]:
        """
        为资源生成检索教材原文证据。

        策略：
        1. 优先从 confirmed 绑定（kp_chunk_links）中取 chunks
        2. 兜底：BM25 检索 course_material_chunks

        Returns:
            {
                "evidence_chunks": List[dict],  # 检索到的 chunks
                "context_text": str,              # 格式化后的 Markdown 上下文
                "has_confirmed_knowledge": bool,
                "coverage": Dict[kp_id, count],
            }
        """
        if not course_id:
            return {
                "evidence_chunks": [],
                "context_text": "",
                "has_confirmed_knowledge": False,
                "coverage": {},
            }

        try:
            from app.repositories.evidence_repo import EvidenceRepository
            from app.rag.retriever import search_knowledge

            evidence_repo = EvidenceRepository()

            all_chunks = []
            coverage: Dict[int, int] = {}

            for kp_id in kp_ids:
                if not kp_id:
                    continue

                # 优先：从 confirmed 绑定中取
                confirmed = evidence_repo.get_confirmed_kp_chunk_links([kp_id], limit=top_k)
                if confirmed:
                    all_chunks.extend(confirmed)
                    coverage[kp_id] = len(confirmed)
                else:
                    # 兜底：BM25 检索
                    kp = evidence_repo.get_kp_by_id(kp_id)
                    if kp:
                        bm25_results = search_knowledge(
                            query=kp["kp_name"],
                            course_id=course_id,
                            top_k=5,
                        )
                        # 补充 kp_id 和相关度分数
                        for chunk in bm25_results:
                            chunk["kp_id"] = kp_id
                            chunk["relevance_score"] = chunk.get("bm25_score", 0.5)
                        all_chunks.extend(bm25_results)
                        coverage[kp_id] = len(bm25_results)
                    else:
                        coverage[kp_id] = 0

            # 去重 + 按相关度排序
            seen = set()
            unique_chunks = []
            for c in all_chunks:
                chunk_id = c.get("chunk_id")
                if chunk_id and chunk_id not in seen:
                    seen.add(chunk_id)
                    unique_chunks.append(c)

            unique_chunks = sorted(
                unique_chunks,
                key=lambda x: float(x.get("relevance_score", 0)),
                reverse=True,
            )[:top_k]

            has_confirmed = any(coverage.get(k, 0) > 0 for k in kp_ids if k)

            return {
                "evidence_chunks": unique_chunks,
                "context_text": self._format_evidence_context(unique_chunks),
                "has_confirmed_knowledge": has_confirmed,
                "coverage": coverage,
            }

        except Exception as e:
            logger.warning("[%s] 证据检索失败 (%s)", self.AGENT_NAME, type(e).__name__)
            return {
                "evidence_chunks": [],
                "context_text": "",
                "has_confirmed_knowledge": False,
                "coverage": {},
            }

    def _format_evidence_context(self, chunks: List[Dict[str, Any]]) -> str:
        """将 chunks 格式化为带来源的 Markdown 上下文。"""
        if not chunks:
            return ""

        lines = ["## 教材原文依据（请确保生成内容与以下原文一致）\n"]
        for i, c in enumerate(chunks, 1):
            source = c.get("filename") or c.get("source", "未知来源")
            page = c.get("source_page")
            paragraph = c.get("source_paragraph")
            location = ""
            if page:
                location = f"第{page}页"
            elif paragraph:
                location = f"第{paragraph}段"

            title = c.get("title", "")
            content = c.get("content", "")
            chunk_id = c.get("chunk_id", "")

            if title:
                lines.append(f"**【证据 {i}】** {title} — {source} {location}")
            else:
                lines.append(f"**【证据 {i}】** {source} {location}")

            # 内容截断至 500 字
            excerpt = content[:500] + ("..." if len(content) > 500 else "")
            lines.append(excerpt)
            lines.append(f"[chunk_id: {chunk_id}]")
            lines.append("")

        return "\n".join(lines)

    def _extract_citations(self, content: str) -> List[str]:
        """从生成内容中提取所有 [引用:chunk_id] 标记。"""
        pattern = re.compile(r'\[引用:(\d+)\]')
        return list(set(pattern.findall(content)))

    def _verify_citations(
        self,
        content: str,
        evidence_chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        校验生成内容中的引用是否都有证据支撑。

        降级策略：
        - 无任何引用 → trustworthiness = draft
        - 引用覆盖率 < 50% → trustworthiness = low
        - 有无效引用 → trustworthiness = medium
        - 正常 → trustworthiness = high
        """
        cited_chunk_ids = self._extract_citations(content)
        valid_chunk_ids = [cid for cid in cited_chunk_ids
                           if any(str(c.get("chunk_id")) == str(cid) for c in evidence_chunks)]
        invalid_chunk_ids = [cid for cid in cited_chunk_ids if cid not in valid_chunk_ids]

        total_citations = len(cited_chunk_ids)
        coverage_ratio = len(valid_chunk_ids) / max(total_citations, 1)

        warnings = []
        if total_citations == 0:
            trustworthiness = "draft"
            warnings.append("未找到教材引用标记，生成内容缺乏来源锚点，标记为草稿")
        elif coverage_ratio < 0.5:
            trustworthiness = "low"
            warnings.append(f"引用覆盖率仅 {coverage_ratio:.0%}，存在引用丢失风险")
        elif invalid_chunk_ids:
            trustworthiness = "medium"
            warnings.append(f"存在无效引用 chunk_ids: {invalid_chunk_ids}，已自动忽略")
        else:
            trustworthiness = "high"

        return {
            "valid_chunk_ids": valid_chunk_ids,
            "invalid_chunk_ids": invalid_chunk_ids,
            "trustworthiness": trustworthiness,
            "warnings": warnings,
            "unfounded_kps": [],  # 后续可扩展：追踪哪些 kp 缺乏引用
        }

    def _build_evidence_links(
        self,
        content: str,
        evidence_chunks: List[Dict[str, Any]],
        kp_ids: List[int],
    ) -> List[Dict[str, Any]]:
        """
        根据生成内容和证据 chunks 构建 evidence_links 记录列表。

        这些记录待写入 resource_evidence_links 表。

        Returns:
            [{
                "chunk_id": int,
                "kp_id": int,
                "quote_text": str,        # 被引用的原文片段
                "relevance_score": float,
                "usage_type": str,         # direct_quote / paraphrase
                "source_page": int | None,
                "source_paragraph": int | None,
            }, ...]
        """
        cited_chunk_ids = set(self._extract_citations(content))
        chunk_map = {str(c.get("chunk_id")): c for c in evidence_chunks}
        links = []

        # 默认 kp_id：取 kp_ids 第一个有效值（兜底）
        default_kp_id = next((k for k in kp_ids if k), 0)

        for chunk_id_str in cited_chunk_ids:
            chunk = chunk_map.get(chunk_id_str)
            if not chunk:
                continue

            content_text = chunk.get("content", "")
            # 引用片段：取原文前 200 字作为 quote_text
            quote_text = content_text[:200] + ("..." if len(content_text) > 200 else "")

            # 判断使用类型：chunk 原文前100字出现在生成内容中 → 直接引用
            usage_type = "paraphrase"
            if content_text[:100] in content:
                usage_type = "direct_quote"

            links.append({
                "chunk_id": int(chunk_id_str),
                "kp_id": chunk.get("kp_id") or default_kp_id,
                "quote_text": quote_text,
                "relevance_score": float(chunk.get("relevance_score", 0.5)),
                "usage_type": usage_type,
                "source_page": chunk.get("source_page"),
                "source_paragraph": chunk.get("source_paragraph"),
            })

        return links

    def _retrieve_rag_for_check(
        self,
        kp_name: str,
        kp_ids: List[int],
        course_id: Optional[int],
    ) -> str:
        """为幻觉检测检索课程知识库上下文。"""
        try:
            from app.services.rag_service import get_context_for_agent
            query = kp_name or "课程知识点"
            context = get_context_for_agent(query=query, course_id=course_id, top_k=5)
            return context if context else ""
        except Exception as e:
            logger.warning(
                "[%s] RAG 检索失败，跳过幻觉检测 (%s)",
                self.AGENT_NAME,
                type(e).__name__,
            )
            return ""

    def _hallucination_check(self, content: str, rag_context: str) -> Optional[Dict[str, Any]]:
        """对比生成内容与知识库，检测幻觉。"""
        import json
        messages = [
            {
                "role": "user",
                "content": PROMPT_HALLUCINATION_CHECK.format(
                    context=rag_context or "（无知识库上下文）",
                    content=content[:2000],
                )
            }
        ]
        try:
            settings = get_settings()
            config = settings.llm_config()
            config.max_tokens = 1024
            llm_result = self.llm_gateway.generate(messages, config)
            if llm_result.status == "failed":
                logger.warning("[%s] 幻觉检测 LLM 调用失败", self.AGENT_NAME)
                return None
            raw = llm_result.content.strip()
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:] if lines[0].startswith("```json") else lines)
                raw = raw.replace("```", "").strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(
                "[%s] 幻觉检测 JSON 解析失败 (%s)",
                self.AGENT_NAME,
                type(e).__name__,
            )
        except Exception as e:
            logger.warning("[%s] 幻觉检测异常 (%s)", self.AGENT_NAME, type(e).__name__)
        return None

    def _call_llm(self, messages: List[Dict[str, str]]) -> Optional[str]:
        if self.llm_gateway is None:
            return None
        try:
            settings = get_settings()
            config = settings.llm_config()
            config.max_tokens = 4096
            llm_result = self.llm_gateway.generate(messages, config)
            if llm_result.status == "failed":
                logger.error("[%s] LLM 调用失败", self.AGENT_NAME)
                return None
            logger.info(f"[{self.AGENT_NAME}] LLM 生成完成，{llm_result.output_tokens} tokens")
            return llm_result.content.strip()
        except Exception as e:
            logger.error("[%s] LLM 调用异常 (%s)", self.AGENT_NAME, type(e).__name__)
        return None

    def _generate_content(
        self,
        kp_name: str,
        resource_type: str,
        difficulty: str,
        evidence_chunks: List[Dict[str, Any]],
    ) -> str:
        """无 LLM 时的兜底生成（不常用）。"""
        evidence_note = ""
        if not evidence_chunks:
            evidence_note = "\n\n> ⚠️ [草稿:缺乏充分教材依据]"

        if resource_type == "lecture":
            return f"""# {kp_name} 专题讲义

## 概述
本讲义帮助学生系统掌握 {kp_name} 相关知识。{evidence_note}

## 核心概念
（以下内容由 EduAgent Studio 智能体生成）

### 关键原理
- 原理一：（由智能体生成）
- 原理二：（由智能体生成）

## 实践应用
（以下包含代码示例和案例分析）

### 示例代码
```sql
-- 由智能体生成相关 SQL 语句
SELECT * FROM table WHERE condition;
```

## 练习题
1. （练习题由智能体生成）
2. （练习题由智能体生成）

---
*由 EduAgent Studio 智能体工作台生成*
"""
        elif resource_type == "quiz":
            return f"""# {kp_name} 练习题

## 选择题

**1. 关于 {kp_name}，以下说法正确的是？**
A. 选项A
B. 选项B
C. 选项C
D. 选项D

**答案：** B

**解析：** （由智能体分析）

---
*由 EduAgent Studio 智能体工作台生成*
"""
        else:
            return f"""# {kp_name} 学习资源

（由 EduAgent Studio 智能体工作台生成）

---
*难度：{difficulty}*
"""
