"""
统一能力注册中心

所有 Tool / Skill / Agent 统一注册，描述 Schema、分类、调用方式。
供两级路由和 Supervisor 循环使用。
"""

import logging
from typing import Any, Callable, Dict, List, Optional, get_type_hints

logger = logging.getLogger(__name__)

# =============================================================================
# Tool 元信息
# =============================================================================

ToolFunc = Callable[..., Any]


class ToolDef:
    """单个能力的定义"""

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        category: str,  # "tool" | "skill" | "agent" | "workflow"
        input_schema: Dict[str, Any],
        output_schema: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        timeout_seconds: int = 60,
        is_async: bool = False,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.tags = tags or []
        self.timeout_seconds = timeout_seconds
        self.is_async = is_async

    def to_openai_schema(self) -> Dict[str, Any]:
        """转换为 OpenAI tool schema 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.id,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


# =============================================================================
# 能力注册表
# =============================================================================

class ToolRegistry:
    """
    统一能力注册中心

    使用示例：
        registry = ToolRegistry()
        registry.register(...)
        pool = registry.select_for_question("帮我出三道题")
        tool_schemas = [t.to_openai_schema() for t in pool]
    """

    def __init__(self):
        self._tools: Dict[str, ToolDef] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}

    # -------------------------------------------------------------------------
    # 注册
    # -------------------------------------------------------------------------

    def register(self, tool: ToolDef, handler: Callable[..., Any]) -> None:
        """注册一个能力"""
        self._tools[tool.id] = tool
        self._handlers[tool.id] = handler
        logger.debug(f"Registered tool: {tool.id} ({tool.category})")

    def register_tool(
        self,
        id: str,
        name: str,
        description: str,
        handler: Callable[..., Any],
        tags: Optional[List[str]] = None,
        timeout: int = 60,
    ) -> None:
        """快捷注册 Tool（原子能力）"""
        self.register(
            ToolDef(
                id=id,
                name=name,
                description=description,
                category="tool",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                },
                tags=tags,
                timeout_seconds=timeout,
            ),
            handler,
        )

    def register_agent(
        self,
        id: str,
        name: str,
        description: str,
        handler: Callable[..., Any],
        input_schema: Dict[str, Any],
        tags: Optional[List[str]] = None,
        timeout: int = 90,
    ) -> None:
        """注册一个 Agent"""
        self.register(
            ToolDef(
                id=id,
                name=name,
                description=description,
                category="agent",
                input_schema=input_schema,
                tags=tags,
                timeout_seconds=timeout,
            ),
            handler,
        )

    # -------------------------------------------------------------------------
    # 查询
    # -------------------------------------------------------------------------

    def get(self, tool_id: str) -> Optional[ToolDef]:
        return self._tools.get(tool_id)

    def get_handler(self, tool_id: str) -> Optional[Callable[..., Any]]:
        return self._handlers.get(tool_id)

    def list_by_category(self, category: str) -> List[ToolDef]:
        return [t for t in self._tools.values() if t.category == category]

    def list_all(self) -> List[ToolDef]:
        return list(self._tools.values())

    def get_openai_schemas(self, tool_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """获取 OpenAI tool schema 列表"""
        tools = [self._tools[tid] for tid in (tool_ids or self._tools.keys()) if tid in self._tools]
        return [t.to_openai_schema() for t in tools]

    # -------------------------------------------------------------------------
    # 两级路由：第一级 — 规则预筛选
    # -------------------------------------------------------------------------

    def select_for_question(self, question: str) -> List[str]:
        """
        根据用户问题，通过规则筛选候选能力 ID 列表。
        这是两级路由的第一级：规则预筛选，不调用 LLM。
        """
        q = question.lower()
        selected: List[str] = []

        # 知识检索 — 大多数问题都需要
        selected.append("retrieve_knowledge")

        # 练习/测验
        if any(w in q for w in ["题", "练习", "测验", "考试", "作业"]):
            selected.append("quiz_agent")

        # 代码/调试
        if any(w in q for w in ["代码", "python", "sql", "java", "debug", "报错", "程序"]):
            selected.append("code_case_agent")

        # 思维导图/结构
        if any(w in q for w in ["思维导图", "结构图", "知识图谱", "整理"]):
            selected.append("mindmap_agent")

        # PPT/课件
        if any(w in q for w in ["ppt", "课件", "幻灯片", "生成"]):
            selected.append("ppt_agent")

        # 语音/音频
        if any(w in q for w in ["朗读", "音频", "语音", "发音"]):
            selected.append("tts_tool")

        # 图片/图解
        if any(w in q for w in ["图片", "示意图", "画图", "图解"]):
            selected.append("image_agent")

        # 学习路径
        if any(w in q for w in ["学习路径", "怎么学", "规划", "路线"]):
            selected.append("planning_agent")

        # 错题分析
        if any(w in q for w in ["错题", "为什么错", "错误原因", "订正"]):
            selected.append("error_analysis_agent")

        # 讲解
        if any(w in q for w in ["讲", "解释", "什么是", "是什么", "原理"]):
            selected.append("explanation_skill")

        # 默认保留知识检索
        if not selected:
            selected.append("retrieve_knowledge")

        return selected[:8]  # 最多8个，避免上下文溢出

    # -------------------------------------------------------------------------
    # 执行
    # -------------------------------------------------------------------------

    async def execute(self, tool_id: str, arguments: Dict[str, Any]) -> Any:
        """执行指定能力"""
        handler = self._handlers.get(tool_id)
        if not handler:
            return {"error": f"Tool not found: {tool_id}"}

        try:
            import asyncio
            if asyncio.iscoroutinefunction(handler):
                return await handler(**arguments)
            else:
                return handler(**arguments)
        except Exception as e:
            logger.error(f"Tool execution failed [{tool_id}]: {e}")
            return {"error": str(e), "tool_id": tool_id}


# =============================================================================
# 全局注册表实例
# =============================================================================

# 全局单例
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        _registry = _build_registry()
    return _registry


def _build_registry() -> ToolRegistry:
    """构建并注册所有能力"""
    from app.services.tutor_tool_handlers import (
        retrieve_knowledge,
        quiz_agent,
        code_case_agent,
        mindmap_agent,
        planning_agent,
        error_analysis_agent,
        explanation_skill,
        image_agent,
        tts_tool,
        ppt_agent,
    )

    registry = ToolRegistry()

    # ── Tool ────────────────────────────────────────────────────────────────
    registry.register_tool(
        id="retrieve_knowledge",
        name="课程知识库检索",
        description="检索课程教材、课件和讲义中的相关片段。当学生提问概念、原理、或需要引用教材原文时使用。输入：course_id, query。输出：相关文档片段列表（含 chunk_id 和原文）。",
        handler=retrieve_knowledge,
        tags=["tool", "knowledge"],
    )

    registry.register_tool(
        id="tts_tool",
        name="语音合成",
        description="将文本转换为语音。适用于学生要求朗读、听音频讲解的场景。",
        handler=tts_tool,
        tags=["tool", "multimodal"],
    )

    registry.register_tool(
        id="image_agent",
        name="图片生成",
        description="根据文本描述生成示意图、流程图或知识配图。适用于学生要求看图、示意图、流程图等场景。",
        handler=image_agent,
        tags=["tool", "multimodal"],
    )

    registry.register_tool(
        id="ppt_agent",
        name="PPT 生成",
        description="根据课程内容和目标生成 PPT 大纲和课件。返回结构化幻灯片 JSON，可直接渲染为 PPT 预览。",
        handler=ppt_agent,
        tags=["tool", "resource"],
        timeout=120,
    )

    # ── Agent ──────────────────────────────────────────────────────────────
    registry.register_agent(
        id="quiz_agent",
        name="自适应题库生成 Agent",
        description="根据知识点和学生画像生成自适应练习题。支持分层练习、诊断题、错题变式。输入：course_id, knowledge_point_ids, question_count, student_profile。输出：题目列表含题目、答案、难度、知识点。",
        handler=quiz_agent,
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "integer"},
                "knowledge_point_ids": {"type": "array", "items": {"type": "integer"}},
                "question_count": {"type": "integer", "default": 3},
                "difficulty": {"type": "string", "enum": ["basic", "intermediate", "advanced"]},
                "student_profile": {"type": "object"},
            },
            "required": ["course_id", "knowledge_point_ids"],
        },
        tags=["agent", "quiz"],
        timeout=90,
    )

    registry.register_agent(
        id="code_case_agent",
        name="代码案例生成 Agent",
        description="根据知识点生成代码实操案例，包含完整代码、运行说明、常见错误分析。输入：course_id, knowledge_point_ids, language_preference。输出：代码案例含代码块、注释、运行步骤。",
        handler=code_case_agent,
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "integer"},
                "knowledge_point_ids": {"type": "array", "items": {"type": "integer"}},
                "language": {"type": "string", "default": "Python"},
                "student_profile": {"type": "object"},
            },
            "required": ["course_id", "knowledge_point_ids"],
        },
        tags=["agent", "code"],
        timeout=90,
    )

    registry.register_agent(
        id="mindmap_agent",
        name="思维导图生成 Agent",
        description="根据知识点结构生成 Markdown/Mermaid 格式的思维导图。输入：knowledge_point_ids, topic。输出：思维导图内容（Markdown 树形结构）。",
        handler=mindmap_agent,
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "integer"},
                "knowledge_point_ids": {"type": "array", "items": {"type": "integer"}},
                "topic": {"type": "string"},
            },
            "required": ["course_id"],
        },
        tags=["agent", "mindmap"],
        timeout=60,
    )

    registry.register_agent(
        id="planning_agent",
        name="学习路径规划 Agent",
        description="根据学生画像和课程知识图谱，规划可解释的学习路径。输入：student_profile, course_id, target_kp_ids。输出：学习步骤列表含知识点、前置依赖、预计时长。",
        handler=planning_agent,
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "integer"},
                "target_kp_ids": {"type": "array", "items": {"type": "integer"}},
                "student_profile": {"type": "object"},
            },
            "required": ["course_id", "student_profile"],
        },
        tags=["agent", "planning"],
        timeout=60,
    )

    registry.register_agent(
        id="error_analysis_agent",
        name="错因分析 Agent",
        description="分析学生的错误模式，判断错误属于概念错误、计算错误、边界错误还是编码错误，并给出针对性讲解。输入：student_profile, error_description, related_kp_ids。输出：错因分析、正确思路、变式题。",
        handler=error_analysis_agent,
        input_schema={
            "type": "object",
            "properties": {
                "student_profile": {"type": "object"},
                "error_description": {"type": "string"},
                "related_kp_ids": {"type": "array", "items": {"type": "integer"}},
            },
            "required": ["error_description"],
        },
        tags=["agent", "error"],
        timeout=60,
    )

    # ── Skill ──────────────────────────────────────────────────────────────
    registry.register_agent(
        id="explanation_skill",
        name="自适应讲解 Skill",
        description="用苏格拉底式提问或类比方式讲解概念。输入：concept, student_level, context。输出：讲解 Markdown 文本。",
        handler=explanation_skill,
        input_schema={
            "type": "object",
            "properties": {
                "concept": {"type": "string"},
                "student_level": {"type": "string"},
                "context": {"type": "string"},
            },
            "required": ["concept"],
        },
        tags=["skill", "explanation"],
        timeout=30,
    )

    return registry
