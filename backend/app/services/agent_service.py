"""智能体工作台 Service — LangGraph 标准版"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

from app.config import get_settings
from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.minimax_provider import MiniMaxProvider
from app.llm.gateway import llm_gateway
from app.services.storage_service import (
    save_resource_content,
    list_storage_files,
)

settings = get_settings()

# 注册 LLM Provider（应用启动时一次性注册）
_llm_registered = False
if not _llm_registered:
    llm_gateway.register_provider("mock", MockProvider())
    llm_gateway.register_provider("openai_compatible", OpenAICompatibleProvider(
        model_name=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    ))
    llm_gateway.register_provider("minimax", MiniMaxProvider(
        model_name=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    ))
    _llm_registered = True

from app.agents.workflow import run_workflow, stream_workflow, get_compiled_graph

_AGENTS = [
    {"id": "diagnosis_agent", "name": "学习诊断智能体", "description": "分析学生薄弱知识点", "type": "diagnosis"},
    {"id": "planning_agent", "name": "资源规划智能体", "description": "生成个性化学习路径", "type": "planning"},
    {"id": "resource_generation_agent", "name": "资源生成智能体", "description": "生成学习资源", "type": "generation"},
    {"id": "assessment_agent", "name": "评测反馈智能体", "description": "分析学习效果", "type": "assessment"},
    {"id": "teacher_review_agent", "name": "教师审核辅助智能体", "description": "生成资源质量建议", "type": "review"},
]


# ---------------------------------------------------------------------------
# 结果字段映射：LangGraph state → 前端期望的字段名
# ---------------------------------------------------------------------------

def _map_workflow_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 LangGraph workflow 返回的原始 state 映射为前端 WorkflowResult 接口格式。

    LangGraph 字段            →  前端字段
    diagnosis                 → diagnosis
    learning_plan             → plan
    generated_resource        → resource
    assessment                → assessment
    teacher_review            → teacher_review_suggestion
    step_history             → metadata.step_history
    quality_score             → metadata.quality_score
    revision_count            → metadata.revision_count
    """
    metadata = dict(raw.get("metadata") or {})
    metadata.update({
        "total_duration_ms": metadata.get("total_duration_ms", 0),
        "step_history": raw.get("step_history", []),
        "quality_score": raw.get("quality_score"),
        "revision_count": raw.get("revision_count", 0),
    })

    return {
        "diagnosis": raw.get("diagnosis"),
        "plan": raw.get("learning_plan"),
        "resource": raw.get("generated_resource"),
        "assessment": raw.get("assessment"),
        "teacher_review_suggestion": raw.get("teacher_review"),
        "metadata": metadata,
        # 原始 state 供高级功能使用
        "_raw": raw,
    }


# ---------------------------------------------------------------------------
# AgentService
# ---------------------------------------------------------------------------

class AgentService:
    """智能体工作台 Service — LangGraph 驱动"""

    def list_agents(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": _AGENTS}

    def _load_knowledge_points(self, course_id: int, kp_ids: List[int], profile_id: int = None) -> List[Dict[str, Any]]:
        """从数据库加载知识点（含掌握度），用于工作流。"""
        try:
            from app.repositories.learning_repo import LearningRepository
            repo = LearningRepository()
            course = repo.get_course(course_id, profile_id=profile_id)
            if not course:
                return []
            all_kps = course.get("knowledge_points") or []
            selected = [kp for kp in all_kps if kp.get("id") in kp_ids]
            return selected
        except Exception as e:
            logger.warning(f"加载知识点失败，使用空列表: {e}")
            return []

    def _load_learning_history(self, student_id: int) -> List[Dict[str, Any]]:
        """从数据库加载学生学习历史（测验/反馈），用于诊断 Agent。"""
        try:
            from app.repositories.learning_feedback_repo import LearningFeedbackRepository
            repo = LearningFeedbackRepository()
            result = repo.list_feedbacks(page=1, page_size=10)
            items = result.get("items") or []
            history = []
            for item in items:
                entry = {
                    "feedback_id": item.get("feedback_id"),
                    "resource_title": item.get("resource_title") or "自主学习",
                    "feedback_type": item.get("feedback_type", "self_report"),
                    "quiz_score": item.get("quiz_score"),
                    "self_mastery": item.get("self_mastery"),
                    "created_at": item.get("created_at", ""),
                }
                history.append(entry)
            return history
        except Exception as e:
            logger.warning(f"加载学习历史失败，使用空列表: {e}")
            return []

    def _resolve_profile(self, student_id: int):
        """解析 student_id → profile_id + student_profile（直接查 repo，避免 FastAPI 依赖）。"""
        try:
            from app.repositories.profile_repo import ProfileRepository
            repo = ProfileRepository()
            items, _ = repo.list_profiles(page=1, page_size=200)
            matched = next((p for p in items if p.get("student_id") == student_id), None)
            if matched:
                profile_id = matched.get("profile_id")
                profile_detail = repo.get_profile(profile_id)
                return profile_id, profile_detail
            return student_id, None
        except Exception as e:
            logger.warning(f"解析 profile 失败: {e}")
            return student_id, None

    def generate(self, req: Any, checkpoint_id: str = None) -> Dict[str, Any]:
        """执行多智能体工作流（LangGraph 标准版）"""
        profile_id, student_profile = self._resolve_profile(req.student_id)
        selected_kps = self._load_knowledge_points(req.course_id, req.knowledge_point_ids, profile_id)
        learning_history = self._load_learning_history(req.student_id)

        raw = run_workflow(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            student_profile=student_profile,
            knowledge_points=selected_kps,
            learning_history=learning_history,
            run_id=None,
            checkpoint_id=checkpoint_id,
        )

        return {"code": 0, "message": "success", "data": _map_workflow_result(raw)}

    def generate_stream(self, req: Any):
        """流式执行工作流，yield 每个步骤的中间结果（SSE 推送）"""
        profile_id, student_profile = self._resolve_profile(req.student_id)
        selected_kps = self._load_knowledge_points(req.course_id, req.knowledge_point_ids, profile_id)
        learning_history = self._load_learning_history(req.student_id)

        return stream_workflow(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            student_profile=student_profile,
            knowledge_points=selected_kps,
            learning_history=learning_history,
        )

    def get_workflow_status(self, run_id: str) -> Dict[str, Any]:
        """查询某个工作流运行的状态（从 Checkpoint 恢复）"""
        graph = get_compiled_graph()
        config = {"configurable": {"thread_id": run_id}}
        state = graph.get_state(config)
        if state and state.values:
            return {"code": 0, "message": "success", "data": _map_workflow_result(state.values)}
        return {"code": 404, "message": "未找到运行记录", "data": None}

    def save_resource(self, req: Any) -> Dict[str, Any]:
        """
        保存学习资源到 storage/ 目录（JSON 格式，含完整元信息）。

        使用已实现的 storage_service，文件存储在 data/storage/{course_id}/YYYY-MM/ 目录。
        """
        raw = req.result.get("_raw", {})
        resource = raw.get("generated_resource") or {}

        title = req.title or resource.get("title", "学习资源")
        content = resource.get("content", "")

        saved = save_resource_content(
            title=title,
            content=content,
            resource_type=req.result.get("resource", {}).get("type", "lecture"),
            course_id=req.course_id,
            metadata={
                "difficulty": resource.get("difficulty"),
                "knowledge_points": resource.get("knowledge_points", []),
                "generation_model": resource.get("generation_metadata", {}).get("model"),
                "quality_score": raw.get("quality_score"),
                "step_history": raw.get("step_history", []),
            },
        )

        return {"code": 0, "message": "资源已保存到学习资源库", "data": saved}

    def list_saved_resources(self, course_id: int = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """列出已保存的资源"""
        result = list_storage_files(course_id=course_id, page=page, page_size=page_size)
        return {"code": 0, "message": "success", "data": result}
