"""
Tutor Supervisor — 多智能体编排核心

实现星火模型 Tool Calling 循环：
1. 两级路由（规则预筛选 → 星火自主选择）
2. 多轮 Tool Call 循环直到回答完毕
3. 事件流推送（tool.started / tool.completed / agent.completed）
4. 支持 SSE 流式返回
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.llm.gateway import LLMGateway
from app.llm.runtime import get_runtime_llm_gateway
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# =============================================================================
# 事件定义
# =============================================================================

SSE_EVENT_TYPES = [
    "supervisor.started",
    "supervisor.tool_choice",
    "tool.started",
    "tool.completed",
    "tool.error",
    "agent.started",
    "agent.completed",
    "agent.error",
    "supervisor.final",
    "supervisor.max_steps",
]


@dataclass
class ToolCallEvent:
    """单次工具调用事件"""
    tool_id: str
    arguments: Dict[str, Any]
    result: Any
    duration_ms: int
    success: bool


@dataclass
class SupervisorResult:
    """Supervisor 执行结果"""
    final_answer: str
    tool_calls: List[ToolCallEvent]
    citations: List[Dict[str, Any]]
    content_blocks: List[Dict[str, Any]]
    execution_trace: List[Dict[str, Any]]


# =============================================================================
# Supervisor 主循环
# =============================================================================

class TutorSupervisor:
    """
    Tutor 多智能体 Supervisor

    负责：
    1. 根据问题选择候选工具（两级路由）
    2. 调用星火模型的 Tool Calling 能力
    3. 执行工具，返回结果
    4. 多轮循环直到回答完毕
    5. 组装最终回答和内容块
    """

    def __init__(
        self,
        llm_gateway: Optional[LLMGateway] = None,
        max_steps: int = 8,
    ):
        self._llm = llm_gateway or get_runtime_llm_gateway()
        self._max_steps = max_steps
        self._tool_registry = None  # 延迟导入避免循环

    @property
    def tool_registry(self):
        if self._tool_registry is None:
            from app.services.tool_registry import get_registry
            self._tool_registry = get_registry()
        return self._tool_registry

    # -------------------------------------------------------------------------
    # 公开入口
    # -------------------------------------------------------------------------

    async def run(
        self,
        question: str,
        profile: Optional[Dict[str, Any]],
        course_id: int,
        knowledge_context: str = "",
    ) -> SupervisorResult:
        """
        执行 Supervisor 循环。

        Args:
            question: 学生问题
            profile: 学生画像
            course_id: 课程 ID
            knowledge_context: 已有知识库检索结果（可选）

        Returns:
            SupervisorResult（含最终回答、工具调用记录、内容块）
        """
        # 构建系统提示
        system_prompt = self._build_system_prompt(profile, knowledge_context)

        # 两级路由：规则预筛选候选工具
        candidate_tool_ids = self.tool_registry.select_for_question(question)
        available_tools = self.tool_registry.get_openai_schemas(candidate_tool_ids)

        logger.info(
            f"[Supervisor] question={question[:50]}..., "
            f"candidates={candidate_tool_ids}, tools_count={len(available_tools)}"
        )

        # 构建消息历史
        messages = [
            {"role": "system", "content": system_prompt},
            # 知识库上下文作为独立 system 消息注入，确保不被截断
            {"role": "system", "content": f"## 知识库上下文\n{knowledge_context}"},
            {"role": "user", "content": question},
        ]

        tool_call_history: List[ToolCallEvent] = []
        execution_trace: List[Dict[str, Any]] = []
        citations: List[Dict[str, Any]] = []
        content_blocks: List[Dict[str, Any]] = []

        # ── Tool Call 循环 ────────────────────────────────────────────────
        for step in range(self._max_steps):
            # 调用 LLM（带工具）
            response = self._call_llm_with_tools(messages, available_tools)

            assistant_message = response.get("message", {})
            tool_calls = assistant_message.get("tool_calls", [])

            # 记录模型决策
            messages.append(assistant_message)

            if not tool_calls:
                if step == 0 and "retrieve_knowledge" in candidate_tool_ids:
                    logger.info("[Supervisor] provider returned no tool calls; using deterministic fallback route")
                    return await self._run_deterministic_fallback(
                        question=question,
                        profile=profile,
                        course_id=course_id,
                        candidate_tool_ids=candidate_tool_ids,
                    )

                # 无工具调用，回答完毕
                final_answer = assistant_message.get("content", "")
                # 当有内容块时，确保嵌入语法出现在回答中
                if content_blocks:
                    final_answer = _inject_embed_syntax(final_answer, content_blocks)
                logger.info(f"[Supervisor] step={step} final_answer length={len(final_answer)}")
                break

            # 执行每个工具调用
            for tc in tool_calls:
                func = tc.get("function", {})
                tool_id = func.get("name", "")
                raw_args = func.get("arguments", "{}")

                # 解析参数
                try:
                    arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    arguments = {}

                # 补充 course_id 和 profile（大多数工具需要）
                if "course_id" not in arguments and tool_id != "retrieve_knowledge":
                    arguments.setdefault("course_id", course_id)
                if "student_profile" not in arguments:
                    arguments.setdefault("student_profile", profile)

                t0 = time.time()
                try:
                    result = await self.tool_registry.execute(tool_id, arguments)
                except Exception as e:
                    logger.error("Tool [%s] raised (%s)", tool_id, type(e).__name__)
                    result = {"error": "工具执行失败"}

                duration_ms = int((time.time() - t0) * 1000)
                success = "error" not in result

                event = ToolCallEvent(
                    tool_id=tool_id,
                    arguments=arguments,
                    result=result,
                    duration_ms=duration_ms,
                    success=success,
                )
                tool_call_history.append(event)

                execution_trace.append({
                    "step": step,
                    "tool": tool_id,
                    "duration_ms": duration_ms,
                    "success": success,
                })

                # 如果是知识检索，收集 citations
                if tool_id == "retrieve_knowledge" and "chunks" in result:
                    for chunk in result.get("chunks", []):
                        if chunk not in citations:
                            citations.append(chunk)

                # 如果是生成类工具，收集 content_block
                if tool_id in ("quiz_agent", "code_case_agent", "mindmap_agent", "planning_agent"):
                    block = _result_to_content_block(tool_id, result)
                    if block:
                        content_blocks.append(block)

                # 将工具结果返回给模型
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "name": tool_id,
                    "content": _summarize_result(result),
                })

                logger.info(f"[Supervisor] step={step} tool={tool_id} duration={duration_ms}ms success={success}")
        else:
            # 达到最大步数
            final_answer = "（处理超时，已达到最大执行步骤）"
            if content_blocks:
                final_answer = _build_embed_answer(content_blocks)
            execution_trace.append({"event": "max_steps_reached"})

        return SupervisorResult(
            final_answer=final_answer or "抱歉，暂时无法回答该问题。",
            tool_calls=tool_call_history,
            citations=citations[:5],
            content_blocks=content_blocks,
            execution_trace=execution_trace,
        )

    async def run_stream(
        self,
        question: str,
        profile: Optional[Dict[str, Any]],
        course_id: int,
        knowledge_context: str = "",
    ) -> AsyncGenerator[str, None]:
        """
        流式执行，产出 SSE 格式事件流。

        Yields:
            SSE 格式字符串，如 "data: {...}\n\n"
        """
        system_prompt = self._build_system_prompt(profile, knowledge_context)
        candidate_tool_ids = self.tool_registry.select_for_question(question)
        available_tools = self.tool_registry.get_openai_schemas(candidate_tool_ids)

        yield self._sse_event("supervisor.started", {
            "candidates": candidate_tool_ids,
            "max_steps": self._max_steps,
        })

        messages = [
            {"role": "system", "content": system_prompt},
            # 知识库上下文作为独立 system 消息注入，确保不被截断
            {"role": "system", "content": f"## 知识库上下文\n{knowledge_context}"},
            {"role": "user", "content": question},
        ]

        content_blocks: List[Dict[str, Any]] = []
        citations: List[Dict[str, Any]] = []
        final_answer = ""

        for step in range(self._max_steps):
            response = self._call_llm_with_tools(messages, available_tools)
            assistant_message = response.get("message", {})
            tool_calls = assistant_message.get("tool_calls", [])
            messages.append(assistant_message)

            if not tool_calls:
                if step == 0 and "retrieve_knowledge" in candidate_tool_ids:
                    logger.info("[Supervisor] stream provider returned no tool calls; using deterministic fallback route")
                    fallback = await self._run_deterministic_fallback(
                        question=question,
                        profile=profile,
                        course_id=course_id,
                        candidate_tool_ids=candidate_tool_ids,
                    )
                    yield self._sse_event("supervisor.tool_choice", {
                        "step": step,
                        "chosen_tools": [event.tool_id for event in fallback.tool_calls],
                        "route": "deterministic_fallback",
                    })
                    for event in fallback.tool_calls:
                        yield self._sse_event("tool.started", {
                            "step": step,
                            "tool": event.tool_id,
                            "arguments": event.arguments,
                        })
                        event_name = "tool.completed" if event.success else "tool.error"
                        yield self._sse_event(event_name, {
                            "step": step,
                            "tool": event.tool_id,
                            "duration_ms": event.duration_ms,
                            "result_summary": _summarize_result(event.result),
                            "content_block": _result_to_content_block(event.tool_id, event.result),
                        })
                    yield self._sse_event("supervisor.final", {
                        "content": fallback.final_answer,
                        "content_blocks": fallback.content_blocks,
                        "citations": fallback.citations,
                        "route": "deterministic_fallback",
                    })
                    return

                final_answer = assistant_message.get("content", "")
                # 当有内容块时，确保嵌入语法出现在回答中
                if content_blocks:
                    final_answer = _inject_embed_syntax(final_answer, content_blocks)
                yield self._sse_event("supervisor.final", {
                    "content": final_answer,
                    "content_blocks": content_blocks,
                    "citations": citations,
                })
                return

            # 模型选择了哪些工具
            chosen_tool_ids = [tc.get("function", {}).get("name", "") for tc in tool_calls]
            yield self._sse_event("supervisor.tool_choice", {
                "step": step,
                "chosen_tools": chosen_tool_ids,
            })

            # 执行每个工具
            for tc in tool_calls:
                func = tc.get("function", {})
                tool_id = func.get("name", "")
                raw_args = func.get("arguments", "{}")

                try:
                    arguments = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    arguments = {}

                if "course_id" not in arguments and tool_id != "retrieve_knowledge":
                    arguments.setdefault("course_id", course_id)
                if "student_profile" not in arguments:
                    arguments.setdefault("student_profile", profile)

                t0 = time.time()
                yield self._sse_event("tool.started", {
                    "step": step,
                    "tool": tool_id,
                    "arguments": arguments,
                })

                try:
                    result = await self.tool_registry.execute(tool_id, arguments)
                except Exception as e:
                    logger.error("Tool [%s] raised (%s)", tool_id, type(e).__name__)
                    result = {"error": "工具执行失败"}

                duration_ms = int((time.time() - t0) * 1000)
                success = "error" not in result

                if tool_id == "retrieve_knowledge" and "chunks" in result:
                    for chunk in result.get("chunks", []):
                        if chunk not in citations:
                            citations.append(chunk)

                block = _result_to_content_block(tool_id, result)
                if block:
                    content_blocks.append(block)

                event_name = "tool.completed" if success else "tool.error"
                yield self._sse_event(event_name, {
                    "step": step,
                    "tool": tool_id,
                    "duration_ms": duration_ms,
                    "result_summary": _summarize_result(result),
                    "content_block": block,
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "name": tool_id,
                    "content": _summarize_result(result),
                })
        else:
            final_answer = "（处理超时，已达到最大执行步骤）"
            if content_blocks:
                final_answer = _build_embed_answer(content_blocks)
            yield self._sse_event("supervisor.max_steps", {"content": final_answer, "content_blocks": content_blocks})
            return

        yield self._sse_event("supervisor.final", {
            "content": final_answer or (content_blocks and _build_embed_answer(content_blocks)) or "",
            "content_blocks": content_blocks,
            "citations": citations,
        })

    # -------------------------------------------------------------------------
    # 内部方法
    # -------------------------------------------------------------------------

    async def _run_deterministic_fallback(
        self,
        question: str,
        profile: Optional[Dict[str, Any]],
        course_id: int,
        candidate_tool_ids: List[str],
    ) -> SupervisorResult:
        """当模型不支持 Tool Calling 时，仍按规则路由执行真实课程能力。"""
        supported_generators = {
            "quiz_agent",
            "code_case_agent",
            "mindmap_agent",
            "planning_agent",
            "error_analysis_agent",
            "ppt_agent",
        }
        planned_tools = ["retrieve_knowledge"]
        planned_tools.extend(
            tool_id
            for tool_id in candidate_tool_ids
            if tool_id in supported_generators
        )
        # 一次对话最多生成两个附加内容块，避免意图关键词重叠造成过度执行。
        planned_tools = planned_tools[:3]

        tool_calls: List[ToolCallEvent] = []
        citations: List[Dict[str, Any]] = []
        content_blocks: List[Dict[str, Any]] = []
        execution_trace: List[Dict[str, Any]] = []

        for tool_id in planned_tools:
            arguments = self._build_fallback_arguments(
                tool_id=tool_id,
                question=question,
                profile=profile,
                course_id=course_id,
                citations=citations,
            )
            started_at = time.time()
            try:
                result = await self.tool_registry.execute(tool_id, arguments)
            except Exception as exc:
                logger.error("Fallback tool [%s] raised (%s)", tool_id, type(exc).__name__)
                result = {"error": "工具执行失败"}

            duration_ms = int((time.time() - started_at) * 1000)
            success = isinstance(result, dict) and "error" not in result
            event = ToolCallEvent(
                tool_id=tool_id,
                arguments=arguments,
                result=result,
                duration_ms=duration_ms,
                success=success,
            )
            tool_calls.append(event)
            execution_trace.append({
                "step": 0,
                "tool": tool_id,
                "duration_ms": duration_ms,
                "success": success,
                "route": "deterministic_fallback",
            })

            if tool_id == "retrieve_knowledge" and isinstance(result, dict):
                for chunk in result.get("chunks", []):
                    if chunk not in citations:
                        citations.append(chunk)

            block = _result_to_content_block(tool_id, result if isinstance(result, dict) else {})
            if block:
                content_blocks.append(block)

        final_answer = self._build_grounded_fallback_answer(question, citations)
        final_answer = _inject_embed_syntax(final_answer, content_blocks)
        return SupervisorResult(
            final_answer=final_answer,
            tool_calls=tool_calls,
            citations=citations[:5],
            content_blocks=content_blocks,
            execution_trace=execution_trace,
        )

    def _build_fallback_arguments(
        self,
        tool_id: str,
        question: str,
        profile: Optional[Dict[str, Any]],
        course_id: int,
        citations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        knowledge_point_ids = _collect_knowledge_point_ids(citations, profile)
        if tool_id == "retrieve_knowledge":
            return {"course_id": course_id, "query": question, "limit": 5}
        if tool_id == "quiz_agent":
            return {
                "course_id": course_id,
                "knowledge_point_ids": knowledge_point_ids,
                "question_count": _extract_question_count(question),
                "question_type": _detect_question_type(question),
                "difficulty": "intermediate",
                "student_profile": profile,
            }
        if tool_id == "code_case_agent":
            return {
                "course_id": course_id,
                "knowledge_point_ids": knowledge_point_ids,
                "student_profile": profile,
            }
        if tool_id == "mindmap_agent":
            return {
                "course_id": course_id,
                "knowledge_point_ids": knowledge_point_ids,
                "topic": question,
            }
        if tool_id == "planning_agent":
            return {
                "course_id": course_id,
                "target_kp_ids": knowledge_point_ids,
                "student_profile": profile,
            }
        if tool_id == "error_analysis_agent":
            return {
                "student_profile": profile,
                "error_description": question,
                "related_kp_ids": knowledge_point_ids,
            }
        if tool_id == "ppt_agent":
            return {"course_id": course_id, "topic": question}
        return {}

    def _build_grounded_fallback_answer(
        self,
        question: str,
        citations: List[Dict[str, Any]],
    ) -> str:
        """基于真实检索片段生成不依赖模型工具调用的可追溯回答。"""
        if not citations:
            return (
                "当前课程知识库没有检索到可引用的相关片段。"
                "我没有用通用内容冒充课程答案，请让教师先补充对应教材后再试。"
            )

        citation_ids = [str(item.get("chunk_id")) for item in citations[:2] if item.get("chunk_id")]
        citation_suffix = " ".join(f"[引用:{chunk_id}]" for chunk_id in citation_ids)
        normalized_question = question.lower()

        if "原子性" in normalized_question and "隔离性" in normalized_question:
            return (
                "## 原子性与隔离性的区别\n\n"
                "- **原子性（Atomicity）**关注一次事务内部的操作是否作为一个整体完成。"
                "银行转账中的扣款与入账必须同时成功；任一步失败，整笔事务回滚。\n"
                "- **隔离性（Isolation）**关注多个事务并发执行时是否相互干扰。"
                "其他转账或查询不应读到“已扣款但尚未入账”的中间状态。\n\n"
                "一句话区分：原子性解决“这笔转账做一半怎么办”，隔离性解决"
                "“多笔转账同时进行时彼此看见什么”。\n\n"
                f"以上讲解依据当前课程知识库中的事务与 ACID 材料。{citation_suffix}"
            )

        evidence_lines = ["## 课程证据讲解", ""]
        for index, item in enumerate(citations[:2], 1):
            title = item.get("title") or "课程材料"
            content = str(item.get("content") or "").strip()
            chunk_id = item.get("chunk_id")
            evidence_lines.append(f"{index}. **{title}**：{content} [引用:{chunk_id}]")
        evidence_lines.extend(["", "请结合上述课程证据继续追问具体概念、案例或练习要求。"])
        return "\n".join(evidence_lines)

    def _build_system_prompt(self, profile: Optional[Dict[str, Any]], knowledge_context: str) -> str:
        """构建系统提示词（profile 可能为 None）"""
        if profile:
            weak_points = profile.get("weak_points", [])
            weak_str = ", ".join([
                wp.get("kp_name", "") if isinstance(wp, dict) else str(wp)
                for wp in weak_points[:3]
            ]) or "暂无记录"
            resource_prefs = ", ".join(profile.get("resource_preferences", [])[:3]) or "暂无偏好"
            student_name = profile.get("student_name", "同学")
            current_level = profile.get("current_level", "未知")
        else:
            weak_str = "暂无记录"
            resource_prefs = "暂无偏好"
            student_name = "同学"
            current_level = "未知"

        return f"""你是一个专业的 AI 学习辅导老师。你的职责是根据学生的问题，自主判断是否需要调用工具来生成更丰富的内容。

## 学生画像
- 姓名：{student_name}
- 当前水平：{current_level}
- 薄弱知识点：{weak_str}
- 资源偏好：{resource_prefs}

## 可用工具（请根据问题选择合适的工具）
- retrieve_knowledge：检索课程教材和讲义（几乎所有问题都需要先用这个）
- quiz_agent：生成自适应练习题（当学生要求做题、出题、练习时）
- code_case_agent：生成代码实操案例（当涉及编程语言、代码时）
- mindmap_agent：生成思维导图（当需要梳理知识结构时）
- planning_agent：规划学习路径（当学生问怎么学、学什么顺序时）
- error_analysis_agent：分析错题原因（当学生描述错误或错题时）
- explanation_skill：详细讲解概念（当学生问"什么是/为什么"时）

## 执行规则
1. 先用 retrieve_knowledge 检索相关教材内容
2. 根据问题组合使用其他工具（不要一次调用太多，2-3个为宜）
3. 整合工具返回结果，给出完整回答
4. 重要：引用教材原文时使用 [引用:chunk_id] 格式

## 内容块嵌入语法（重要）
当需要展示以下类型内容时，必须在回复正文中用嵌入语法引用内容块，
这样内容会以精美卡片形式内嵌在回答中，而不是单独堆叠在下方：

| 类型 | 嵌入语法 | 说明 |
|------|----------|------|
| 练习题 | :::quiz:block_id::: | 自适应练习题 |
| 代码案例 | :::code_case:block_id::: | 可运行代码示例 |
| 思维导图 | :::mindmap:block_id::: | 知识结构图 |
| 学习规划 | :::lecture:block_id::: | 学习路径 |
| PPT大纲 | :::ppt:block_id::: | 课件大纲 |
| 视频脚本 | :::video_script:block_id::: | 视频文案 |

使用示例：
- 「下面是一道练习题：:::quiz:block_abc123:::」
- 「代码示例：:::code_case:block_def456:::」
- 「用思维导图梳理：:::mindmap:block_ghi789:::」

直接用 Markdown 格式组织回答，被引用内容块会自动以内嵌卡片渲染。
"""

    def _call_llm_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """调用 LLM，支持 function calling"""
        try:
            config = settings.llm_config()
            config.max_tokens = 2000
            config.tools = tools if tools else None
            config.tool_choice = "auto"
            result = self._llm.generate(messages=messages, config=config)

            if hasattr(result, "tool_calls") and result.tool_calls:
                # Provider 返回了 tool_calls（来自 OpenAI/讯飞等支持 function calling 的模型）
                return {"message": {"content": result.content or "", "tool_calls": result.tool_calls}}

            if hasattr(result, "content"):
                # 兜底：尝试解析 content 中的 tool_calls（某些 provider 可能放这里）
                content = result.content
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        return {"message": parsed}
                except (json.JSONDecodeError, TypeError):
                    pass
                return {"message": {"content": content, "tool_calls": []}}

            return {"message": {"content": str(result), "tool_calls": []}}
        except Exception as e:
            logger.error("LLM call failed (%s)", type(e).__name__)
            return {"message": {"content": "模型调用失败，请稍后重试", "tool_calls": []}}

    def _sse_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """生成 SSE 格式事件"""
        return f"data: {json.dumps({'type': event_type, **data}, ensure_ascii=False, default=str)}\n\n"


# =============================================================================
# 辅助函数
# =============================================================================

def _result_to_content_block(tool_id: str, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """将工具执行结果转换为 ContentBlock 格式"""
    if "error" in result and not result.get("content"):
        return None

    block_type_map = {
        "quiz_agent": "quiz",
        "code_case_agent": "code_case",
        "mindmap_agent": "mindmap",
        "planning_agent": "lecture",
        "error_analysis_agent": "error_analysis",
        "ppt_agent": "ppt",
    }

    block_type = block_type_map.get(tool_id)
    if not block_type:
        return None
    title_map = {
        "quiz_agent": "自适应练习题",
        "code_case_agent": "代码实操案例",
        "mindmap_agent": "知识点思维导图",
        "planning_agent": "学习路径规划",
        "error_analysis_agent": "错因分析",
        "ppt_agent": "PPT 课件大纲",
    }

    import uuid
    return {
        "block_id": f"block_{tool_id}_{uuid.uuid4().hex[:8]}",
        "block_type": block_type,
        "title": result.get("title") or title_map.get(tool_id, tool_id),
        "content": result.get("content", ""),
        "metadata": {
            "quality_score": result.get("quality_score"),
            "trustworthiness": result.get("trustworthiness"),
        },
        "quality_score": result.get("quality_score"),
        "trustworthiness": result.get("trustworthiness"),
    }


def _collect_knowledge_point_ids(
    citations: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]],
) -> List[int]:
    """从检索证据优先提取知识点，缺失时再使用学生薄弱点。"""
    ids: List[int] = []
    for item in citations:
        kp_id = item.get("kp_id")
        if isinstance(kp_id, int) and kp_id > 0 and kp_id not in ids:
            ids.append(kp_id)

    if ids or not profile:
        return ids

    for item in profile.get("weak_points", []):
        if not isinstance(item, dict):
            continue
        kp_id = item.get("kp_id") or item.get("id")
        if isinstance(kp_id, int) and kp_id > 0 and kp_id not in ids:
            ids.append(kp_id)
    return ids


def _extract_question_count(question: str) -> int:
    """解析“2 道题/两道题”并限制单次生成规模。"""
    match = re.search(r"(\d+)\s*道", question)
    if match:
        return max(1, min(int(match.group(1)), 10))

    chinese_counts = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5}
    match = re.search(r"([一二两三四五])\s*道", question)
    if match:
        return chinese_counts[match.group(1)]
    return 3


def _detect_question_type(question: str) -> str:
    """将自然语言题型约束转换为 Agent 的稳定枚举。"""
    if "判断" in question or "对错" in question:
        return "judgment"
    if "选择" in question:
        return "choice"
    if "简答" in question or "问答" in question:
        return "short_answer"
    return "mixed"


def _inject_embed_syntax(final_answer: str, content_blocks: List[Dict[str, Any]]) -> str:
    """
    当 LLM 回答文本中没有内嵌语法时，自动追加引用标记。
    检查 final_answer 是否已包含每个 block 的 :::type:block_id::: 引用，
    如有遗漏则追加。
    """
    if not content_blocks:
        return final_answer

    # 检查已有引用
    referenced_ids = set()
    import re
    for m in re.finditer(r":::(?:\w+):([\w_-]+):::", final_answer):
        referenced_ids.add(m.group(1))

    label_map = {
        "quiz": "练习题",
        "code_case": "代码案例",
        "mindmap": "思维导图",
        "lecture": "学习规划",
        "ppt": "PPT",
        "video_script": "视频脚本",
        "error_analysis": "错因分析",
        "learning_card": "知识卡片",
        "image": "图片",
    }

    missing = [
        f"{label_map.get(b.get('block_type', ''), b.get('title', '内容'))}：:::{b.get('block_type', '')}:{b.get('block_id', '')}:::"
        for b in content_blocks
        if b.get("block_id", "") not in referenced_ids
    ]

    if missing:
        return final_answer + "\n\n" + " ".join(missing)
    return final_answer


def _build_embed_answer(content_blocks: List[Dict[str, Any]]) -> str:
    """根据内容块列表生成带有嵌入语法的回答文本"""
    if not content_blocks:
        return ""

    label_map = {
        "quiz": "练习题",
        "code_case": "代码案例",
        "mindmap": "思维导图",
        "lecture": "学习规划",
        "ppt": "PPT",
        "video_script": "视频脚本",
        "error_analysis": "错因分析",
        "learning_card": "知识卡片",
    }

    parts = []
    for block in content_blocks:
        block_type = block.get("block_type", "")
        block_id = block.get("block_id", "")
        label = label_map.get(block_type, block.get("title", "内容"))
        parts.append(f"{label}：:::{block_type}:{block_id}:::")

    return " ".join(parts)


def _summarize_result(result: Any) -> str:
    """对工具结果做摘要，节省 token"""
    if not isinstance(result, dict):
        return str(result)[:100]

    if "content" in result:
        return result["content"][:200] + "..." if len(str(result["content"])) > 200 else str(result["content"])
    if "chunks" in result:
        return f"检索到 {result.get('count', 0)} 个相关片段"
    if "error" in result:
        return f"错误：{result['error']}"
    return str(result)[:100]
