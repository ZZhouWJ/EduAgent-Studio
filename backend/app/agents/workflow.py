"""
多智能体工作流 — LangGraph 标准 StateGraph 实现

架构说明：
- StateGraph：标准 LangGraph 状态图，支持条件路由、循环、自检
- Supervisor 节点：编排器，根据当前状态决定下一步走哪个 Agent
- Checkpointer：SQLite 持久化，支持暂停/恢复工作流
- 每个 Agent 节点：无状态函数，从 state 读取输入，往 state 写入结果
- 创新点：
  1. 条件路由 — 资源质量不达标时自动返工（revisit 循环）
  2. Supervisor 编排 — 非线性执行，支持跳过/重试
  3. 状态持久化 — 每步结果落盘，支持断点恢复
  4. 流式反馈 — 每个 Agent 完成时 yield 中间结果
"""

from __future__ import annotations

import logging
import os
import sqlite3
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver

from app.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. 状态模式（Schema）
# ---------------------------------------------------------------------------


class WorkflowStep(str, Enum):
    """工作流当前步骤枚举"""
    INIT = "init"
    DIAGNOSIS = "diagnosis"
    PLANNING = "planning"
    GENERATION = "generation"
    ASSESSMENT = "assessment"
    TEACHER_REVIEW = "teacher_review"
    REVISION = "revision"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowState(TypedDict, total=False):
    """
    LangGraph 全局状态。

    创新设计：
    - step_history: 记录每个 Agent 的执行历史（支持审计 + 回退）
    - revision_count: 返工计数，超过阈值后停止循环
    - quality_score: 教师审核质量评分，用于条件路由
    - needs_revision: 由 Supervisor 判断是否需要返工
    - metadata: 工作流元信息（耗时、错误等）
    """

    # === 输入参数 ===
    run_id: str
    student_id: int
    course_id: int
    knowledge_point_ids: List[int]
    resource_type: str
    difficulty: str
    student_profile: Optional[Dict[str, Any]]
    knowledge_points: Optional[List[Dict[str, Any]]]
    learning_history: Optional[List[Dict[str, Any]]]

    # === 各 Agent 输出 ===
    diagnosis: Optional[Dict[str, Any]]
    learning_plan: Optional[Dict[str, Any]]
    generated_resource: Optional[Dict[str, Any]]
    assessment: Optional[Dict[str, Any]]
    teacher_review: Optional[Dict[str, Any]]
    evidence_links: Optional[List[Dict[str, Any]]]  # 资源-证据关联，待写入 DB
    trustworthiness: Optional[str]  # 可信度等级：high/medium/low/draft

    # === 工作流控制 ===
    current_step: str
    step_history: List[Dict[str, Any]]  # [{step, status, timestamp, error, duration_ms}]
    revision_count: int
    quality_score: Optional[float]
    needs_revision: bool
    revision_reason: Optional[str]

    # === 元信息 ===
    metadata: Dict[str, Any]  # {total_duration_ms, error, warnings, ...}


def _make_step_record(
    step: WorkflowStep,
    status: Literal["success", "failed", "skipped"] = "success",
    error: Optional[str] = None,
    duration_ms: int = 0,
) -> Dict[str, Any]:
    return {
        "step": step.value,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "error": error,
        "duration_ms": duration_ms,
    }


# ---------------------------------------------------------------------------
# 2. Agent 节点函数（LangGraph 规范：无状态，接收 state，返回 dict 增量更新）
# ---------------------------------------------------------------------------

def _diagnosis_node(state: WorkflowState) -> Dict[str, Any]:
    """节点 1：学习诊断"""
    from app.agents.diagnosis_agent import DiagnosisAgent
    import time

    settings = get_settings()
    llm_gateway = _get_llm_gateway()
    agent = DiagnosisAgent(llm_gateway)

    start = time.time()
    try:
        result = agent.run(
            student_profile=state.get("student_profile") or {},
            knowledge_points=state.get("knowledge_points") or [],
            learning_history=state.get("learning_history") or [],
        )
        duration = int((time.time() - start) * 1000)
        return {
            "diagnosis": result,
            "current_step": WorkflowStep.DIAGNOSIS.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.DIAGNOSIS, "success", duration_ms=duration)
            ],
        }
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(f"[DiagnosisNode] {e}")
        return {
            "diagnosis": None,
            "current_step": WorkflowStep.FAILED.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.DIAGNOSIS, "failed", str(e), duration)
            ],
            "metadata": {**state.get("metadata", {}), "diagnosis_error": str(e)},
        }


def _planning_node(state: WorkflowState) -> Dict[str, Any]:
    """节点 2：学习规划"""
    from app.agents.planning_agent import PlanningAgent
    import time

    start = time.time()
    try:
        agent = PlanningAgent(_get_llm_gateway())
        result = agent.run(
            diagnosis=state.get("diagnosis") or {},
            learning_goal=state.get("student_profile", {}).get("learning_goal", ""),
            course_outline=state.get("knowledge_points") or [],
            student_profile=state.get("student_profile") or {},
        )
        duration = int((time.time() - start) * 1000)
        return {
            "learning_plan": result,
            "current_step": WorkflowStep.PLANNING.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.PLANNING, "success", duration_ms=duration)
            ],
        }
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(f"[PlanningNode] {e}")
        return {
            "current_step": WorkflowStep.FAILED.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.PLANNING, "failed", str(e), duration)
            ],
            "metadata": {**state.get("metadata", {}), "planning_error": str(e)},
        }


def _resource_generation_node(state: WorkflowState) -> Dict[str, Any]:
    """节点 3：资源生成"""
    from app.agents.resource_generation_agent import ResourceGenerationAgent
    import time

    start = time.time()
    try:
        agent = ResourceGenerationAgent(_get_llm_gateway())
        result = agent.run(
            learning_path=state.get("learning_plan", {}).get("learning_path", []),
            resource_type=state.get("resource_type", "lecture"),
            difficulty=state.get("difficulty", "intermediate"),
            student_profile=state.get("student_profile") or {},
            course_id=state.get("course_id"),
        )
        duration = int((time.time() - start) * 1000)

        # 从生成结果中提取 evidence_links 和 trustworthiness
        evidence_links = result.get("evidence_links", [])
        trustworthiness = result.get("trustworthiness", "draft")

        return {
            "generated_resource": result,
            "evidence_links": evidence_links,
            "trustworthiness": trustworthiness,
            "current_step": WorkflowStep.GENERATION.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.GENERATION, "success", duration_ms=duration)
            ],
        }
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(f"[ResourceGenerationNode] {e}")
        return {
            "current_step": WorkflowStep.FAILED.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.GENERATION, "failed", str(e), duration)
            ],
            "metadata": {**state.get("metadata", {}), "generation_error": str(e)},
        }


def _assessment_node(state: WorkflowState) -> Dict[str, Any]:
    """节点 4：学习评测"""
    from app.agents.assessment_agent import AssessmentAgent
    import time

    start = time.time()
    try:
        agent = AssessmentAgent(_get_llm_gateway())
        result = agent.run(
            test_results=None,
            learning_feedback=None,
            generated_resource=state.get("generated_resource"),
            student_profile=state.get("student_profile"),
        )
        duration = int((time.time() - start) * 1000)
        return {
            "assessment": result,
            "current_step": WorkflowStep.ASSESSMENT.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.ASSESSMENT, "success", duration_ms=duration)
            ],
        }
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(f"[AssessmentNode] {e}")
        return {
            "current_step": WorkflowStep.FAILED.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.ASSESSMENT, "failed", str(e), duration)
            ],
            "metadata": {**state.get("metadata", {}), "assessment_error": str(e)},
        }


def _teacher_review_node(state: WorkflowState) -> Dict[str, Any]:
    """节点 5：教师审核"""
    from app.agents.teacher_review_agent import TeacherReviewAgent
    import time

    start = time.time()
    try:
        agent = TeacherReviewAgent(_get_llm_gateway())
        result = agent.run(
            generated_resource=state.get("generated_resource") or {},
            difficulty_requirement=state.get("difficulty", "intermediate"),
        )
        duration = int((time.time() - start) * 1000)
        quality_score = result.get("quality_score")
        needs_revision = quality_score is not None and quality_score < 7.0

        return {
            "teacher_review": result,
            "quality_score": quality_score,
            "needs_revision": needs_revision,
            "revision_reason": f"质量评分 {quality_score}/10 < 7.0 阈值" if needs_revision else None,
            "current_step": WorkflowStep.TEACHER_REVIEW.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.TEACHER_REVIEW, "success", duration_ms=duration)
            ],
        }
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(f"[TeacherReviewNode] {e}")
        return {
            "current_step": WorkflowStep.FAILED.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.TEACHER_REVIEW, "failed", str(e), duration)
            ],
            "metadata": {**state.get("metadata", {}), "review_error": str(e)},
        }


def _revision_node(state: WorkflowState) -> Dict[str, Any]:
    """节点 6：返工节点 — 基于审核反馈重新生成资源"""
    from app.agents.resource_generation_agent import ResourceGenerationAgent
    import time

    start = time.time()
    revision_count = state.get("revision_count", 0) + 1

    review = state.get("teacher_review", {})
    suggestions = review.get("suggestions", [])
    risk_alerts = review.get("risk_alerts", [])

    try:
        agent = ResourceGenerationAgent(_get_llm_gateway())
        enhanced_prompt_context = (
            f"\n\n## 返工要求（第{revision_count}次返工）\n"
            f"上次审核发现问题：{state.get('revision_reason', '质量不达标')}\n"
            f"具体建议：{'；'.join(suggestions)}\n"
            f"风险提示：{'；'.join(a.get('message', '') for a in risk_alerts)}\n"
        )

        original_content = state.get("generated_resource", {}).get("content", "")
        enhanced_resource = agent.run(
            learning_path=state.get("learning_plan", {}).get("learning_path", []),
            resource_type=state.get("resource_type", "lecture"),
            difficulty=state.get("difficulty", "intermediate"),
            student_profile={
                **(state.get("student_profile") or {}),
                "_revision_context": enhanced_prompt_context,
                "_original_content": original_content[:500],
            },
            course_id=state.get("course_id"),
        )
        duration = int((time.time() - start) * 1000)
        return {
            "generated_resource": enhanced_resource,
            "evidence_links": enhanced_resource.get("evidence_links", []),
            "trustworthiness": enhanced_resource.get("trustworthiness", "draft"),
            "revision_count": revision_count,
            "current_step": WorkflowStep.REVISION.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.REVISION, "success", duration_ms=duration)
            ],
        }
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(f"[RevisionNode] {e}")
        return {
            "revision_count": revision_count,
            "current_step": WorkflowStep.FAILED.value,
            "step_history": state.get("step_history", []) + [
                _make_step_record(WorkflowStep.REVISION, "failed", str(e), duration)
            ],
            "metadata": {**state.get("metadata", {}), "revision_error": str(e)},
        }


# ---------------------------------------------------------------------------
# 3. Supervisor 路由函数（条件边）
# ---------------------------------------------------------------------------

def _supervisor_router(state: WorkflowState) -> Literal[
    "diagnosis", "planning", "generation", "assessment", "teacher_review",
    "revision", "completed"
]:
    """
    Supervisor 编排策略（非线性路由）：

    创新点：
    - 基于状态机的条件路由，不是简单顺序执行
    - 每个步骤完成后由 Supervisor 决定下一步
    - 资源质量不达标时触发返工循环（最多 3 次）
    - 任何一个 Agent 失败后跳到最终状态并报错
    """
    step = state.get("current_step", WorkflowStep.INIT.value)
    metadata = state.get("metadata", {})

    if any(metadata.get(f"{k}_error") for k in
           ["diagnosis_error", "planning_error", "generation_error",
            "assessment_error", "review_error"]):
        return "completed"

    if step == WorkflowStep.INIT.value:
        return "diagnosis"

    if step == WorkflowStep.DIAGNOSIS.value:
        return "planning"

    if step == WorkflowStep.PLANNING.value:
        return "generation"

    if step == WorkflowStep.GENERATION.value:
        return "assessment"

    if step == WorkflowStep.ASSESSMENT.value:
        return "teacher_review"

    if step == WorkflowStep.TEACHER_REVIEW.value:
        needs_revision = state.get("needs_revision", False)
        revision_count = state.get("revision_count", 0)

        if needs_revision and revision_count < 3:
            return "revision"

        return "completed"

    if step == WorkflowStep.REVISION.value:
        return "teacher_review"

    return "completed"


# ---------------------------------------------------------------------------
# 4. 辅助函数
# ---------------------------------------------------------------------------

def _get_llm_gateway():
    """懒加载 LLM Gateway，延迟注入避免循环导入"""
    from app.llm import llm_gateway as _gw
    return _gw


# ---------------------------------------------------------------------------
# 5. LangGraph StateGraph 工厂
# ---------------------------------------------------------------------------

_checkpointer: Optional[InMemorySaver] = None


def _get_checkpointer() -> InMemorySaver:
    """单例 Checkpointer — 内存持久化工作流状态"""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = InMemorySaver()
        logger.info("Checkpointer initialized (InMemory)")
    return _checkpointer


def build_learning_agent_graph() -> StateGraph:
    """
    构建并返回 LangGraph StateGraph。

    创新点：
    1. Supervisor 路由模式 — 非线性条件执行
    2. 返工循环 — 质量评分 < 7 时自动返工（最多 3 次）
    3. 步骤历史记录 — 每个 Agent 执行记录可审计
    4. SQLite Checkpoint — 暂停/恢复能力
    5. 失败容错 — 单步失败不导致整体崩溃
    """
    graph = StateGraph(WorkflowState)

    # 注册所有节点
    graph.add_node("supervisor", lambda s: s)
    graph.add_node("diagnosis", _diagnosis_node)
    graph.add_node("planning", _planning_node)
    graph.add_node("generation", _resource_generation_node)
    graph.add_node("assessment", _assessment_node)
    graph.add_node("teacher_review", _teacher_review_node)
    graph.add_node("revision", _revision_node)

    # 入口：START → supervisor
    graph.add_edge(START, "supervisor")

    # 条件边：supervisor 根据路由函数决定下一个节点
    graph.add_conditional_edges(
        "supervisor",
        _supervisor_router,
        {
            "diagnosis": "diagnosis",
            "planning": "planning",
            "generation": "generation",
            "assessment": "assessment",
            "teacher_review": "teacher_review",
            "revision": "revision",
            "completed": END,
        },
    )

    # 节点完成后 → 返回 supervisor 再路由
    for node in ["diagnosis", "planning", "generation", "assessment", "teacher_review", "revision"]:
        graph.add_edge(node, "supervisor")

    # 编译：附加 checkpointer 和配置
    checkpointer = _get_checkpointer()
    compiled = graph.compile(checkpointer=checkpointer)

    logger.info("LearningAgentGraph compiled successfully")
    return compiled


# ---------------------------------------------------------------------------
# 6. 高层 API：执行工作流
# ---------------------------------------------------------------------------

_compiled_graph: Optional[StateGraph] = None


def get_compiled_graph() -> StateGraph:
    """获取编译后的图（单例）"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_learning_agent_graph()
    return _compiled_graph


def run_workflow(
    student_id: int,
    course_id: int,
    knowledge_point_ids: List[int],
    resource_type: str,
    difficulty: str,
    student_profile: Optional[Dict[str, Any]] = None,
    knowledge_points: Optional[List[Dict[str, Any]]] = None,
    learning_history: Optional[List[Dict[str, Any]]] = None,
    run_id: Optional[str] = None,
    checkpoint_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    执行完整的多智能体工作流。

    Args:
        run_id: 可选的运行 ID，用于断点恢复
        checkpoint_id: 从 SQLite Checkpoint 恢复的 thread_id

    Returns:
        最终状态字典（包含所有 Agent 输出 + metadata）
    """
    graph = get_compiled_graph()

    initial_state: WorkflowState = {
        "run_id": run_id or f"run-{uuid.uuid4().hex[:12]}",
        "student_id": student_id,
        "course_id": course_id,
        "knowledge_point_ids": knowledge_point_ids,
        "resource_type": resource_type,
        "difficulty": difficulty,
        "student_profile": student_profile,
        "knowledge_points": knowledge_points,
        "learning_history": learning_history,
        "diagnosis": None,
        "learning_plan": None,
        "generated_resource": None,
        "assessment": None,
        "teacher_review": None,
        "evidence_links": [],
        "current_step": WorkflowStep.INIT.value,
        "step_history": [],
        "revision_count": 0,
        "quality_score": None,
        "needs_revision": False,
        "revision_reason": None,
        "metadata": {},
    }

    import time
    total_start = time.time()

    # 根据是否有 checkpoint_id 决定是恢复还是新建运行
    if checkpoint_id:
        config = {"configurable": {"thread_id": checkpoint_id}}
        final_state = graph.get_state(config)
        result = final_state.values if final_state else initial_state
    else:
        config = {
            "configurable": {
                "thread_id": initial_state["run_id"],
            }
        }
        result = graph.invoke(initial_state, config)

    total_duration_ms = int((time.time() - total_start) * 1000)
    result["metadata"] = {
        **result.get("metadata", {}),
        "total_duration_ms": total_duration_ms,
        "revision_count": result.get("revision_count", 0),
        "run_id": result.get("run_id"),
    }
    result["current_step"] = WorkflowStep.COMPLETED.value

    logger.info(
        f"[Workflow] run_id={result.get('run_id')} completed in {total_duration_ms}ms, "
        f"revisions={result.get('revision_count', 0)}, "
        f"quality_score={result.get('quality_score')}"
    )

    return result


def stream_workflow(
    student_id: int,
    course_id: int,
    knowledge_point_ids: List[int],
    resource_type: str,
    difficulty: str,
    student_profile: Optional[Dict[str, Any]] = None,
    knowledge_points: Optional[List[Dict[str, Any]]] = None,
    learning_history: Optional[List[Dict[str, Any]]] = None,
    run_id: Optional[str] = None,
):
    """
    流式执行工作流，yield 每个步骤的中间结果。

    创新点：支持 SSE/Server-Sent-Events 流式推送中间结果，
    前端可以实时显示每个 Agent 的执行状态。
    """
    graph = get_compiled_graph()

    initial_state: WorkflowState = {
        "run_id": run_id or f"run-{uuid.uuid4().hex[:12]}",
        "student_id": student_id,
        "course_id": course_id,
        "knowledge_point_ids": knowledge_point_ids,
        "resource_type": resource_type,
        "difficulty": difficulty,
        "student_profile": student_profile,
        "knowledge_points": knowledge_points,
        "learning_history": learning_history,
        "diagnosis": None,
        "learning_plan": None,
        "generated_resource": None,
        "assessment": None,
        "teacher_review": None,
        "evidence_links": [],
        "current_step": WorkflowStep.INIT.value,
        "step_history": [],
        "revision_count": 0,
        "quality_score": None,
        "needs_revision": False,
        "revision_reason": None,
        "metadata": {},
    }

    config = {
        "configurable": {
            "thread_id": initial_state["run_id"],
        }
    }

    for event in graph.stream(initial_state, config):
        node_name = next(iter(event.keys()))
        node_state = event[node_name]
        step_name = node_state.get("current_step", node_name)

        yield {
            "node": node_name,
            "step": step_name,
            "revision_count": node_state.get("revision_count", 0),
            "quality_score": node_state.get("quality_score"),
            "needs_revision": node_state.get("needs_revision", False),
            "has_diagnosis": node_state.get("diagnosis") is not None,
            "has_plan": node_state.get("learning_plan") is not None,
            "has_resource": node_state.get("generated_resource") is not None,
            "has_assessment": node_state.get("assessment") is not None,
            "has_review": node_state.get("teacher_review") is not None,
            "step_history": node_state.get("step_history", []),
            "metadata": node_state.get("metadata", {}),
        }

    # Yield final result on completion
    final_state = graph.get_state(config)
    if final_state and final_state.values:
        result = final_state.values
        result["metadata"] = {
            **result.get("metadata", {}),
            "total_duration_ms": result.get("metadata", {}).get("total_duration_ms", 0),
            "revision_count": result.get("revision_count", 0),
        }
        result["current_step"] = "completed"
        yield {
            "type": "done",
            "result": {
                "diagnosis": result.get("diagnosis"),
                "plan": result.get("learning_plan"),
                "resource": result.get("generated_resource"),
                "assessment": result.get("assessment"),
                "teacher_review_suggestion": result.get("teacher_review"),
                "evidence_links": result.get("evidence_links", []),
                "trustworthiness": result.get("trustworthiness", "draft"),
                "metadata": result.get("metadata"),
            },
        }
    else:
        yield {"type": "done", "result": None}
