"""智能体工作台 Service — LangGraph 标准版"""
import logging
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


def _map_workflow_result(raw: Dict[str, Any]) -> Dict[str, Any]:
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
        "evidence_links": raw.get("evidence_links", []),
        "trustworthiness": raw.get("trustworthiness", "draft"),
        "metadata": metadata,
        "_raw": raw,
    }


class AgentService:
    """智能体工作台 Service — LangGraph 驱动"""

    def list_agents(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": _AGENTS}

    def _load_knowledge_points(self, course_id: int, kp_ids: List[int], profile_id: int = None) -> List[Dict[str, Any]]:
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
        try:
            from app.repositories.profile_repo import ProfileRepository
            repo = ProfileRepository()
            profile = repo.get_profile_by_student_id(student_id)
            if profile:
                return profile.get("profile_id"), profile
            return student_id, None
        except Exception as e:
            logger.warning(f"解析 profile 失败: {e}")
            return student_id, None

    def generate(self, req: Any, checkpoint_id: str = None) -> Dict[str, Any]:
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
        graph = get_compiled_graph()
        config = {"configurable": {"thread_id": run_id}}
        state = graph.get_state(config)
        if state and state.values:
            return {"code": 0, "message": "success", "data": _map_workflow_result(state.values)}
        return {"code": 404, "message": "未找到运行记录", "data": None}

    def save_resource(self, req: Any, user_id: int = 0) -> Dict[str, Any]:
        raw = req.result.get("_raw", {})
        resource = raw.get("generated_resource") or {}
        evidence_links = raw.get("evidence_links", [])
        trustworthiness = raw.get("trustworthiness", "draft")

        title = req.title or resource.get("title", "学习资源")
        content = resource.get("content", "")

        # 保存到 learning_resources 表（主表，有 resource_id）
        try:
            from app.repositories.learning_resource_repo import LearningResourceRepository
            lr_repo = LearningResourceRepository()
            db_resource = lr_repo.create_resource(
                data={
                    "course_id": req.course_id,
                    "resource_title": title,
                    "resource_type": req.result.get("resource", {}).get("type", "lecture"),
                    "difficulty": resource.get("difficulty", "intermediate"),
                    "content": content,
                    "target_kp_ids": resource.get("knowledge_points", []),
                    "generation_model": resource.get("generation_metadata", {}).get("model"),
                    "generation_agent": resource.get("generation_metadata", {}).get("agent"),
                    "status": "pending_review",
                },
                created_by=user_id,
            )
            saved_resource_id = db_resource.get("resource_id")
            logger.info(f"[AgentService] 资源写入 learning_resources: resource_id={saved_resource_id}")
        except Exception as e:
            logger.warning(f"[AgentService] 写入 learning_resources 失败: {e}")
            saved_resource_id = None

        # 同时保存到文件存储（保留原有逻辑）
        saved = save_resource_content(
            title=title,
            content=content,
            resource_type=req.result.get("resource", {}).get("type", "lecture"),
            course_id=req.course_id,
            metadata={
                "difficulty": resource.get("difficulty"),
                "knowledge_points": resource.get("knowledge_points", []),
                "target_kp_ids": resource.get("target_kp_ids", ""),
                "generation_model": resource.get("generation_metadata", {}).get("model"),
                "quality_score": raw.get("quality_score"),
                "step_history": raw.get("step_history", []),
                "trustworthiness": trustworthiness,
                "db_resource_id": saved_resource_id,
            },
        )

        # 如果有 db_resource_id，则写入 evidence_links
        if saved_resource_id and evidence_links:
            try:
                from app.repositories.evidence_repo import EvidenceRepository
                ev_repo = EvidenceRepository()
                for link in evidence_links:
                    link["resource_id"] = saved_resource_id
                ev_repo.insert_resource_evidence_links(evidence_links)
                logger.info(f"[AgentService] 写入 {len(evidence_links)} 条 evidence_links，resource_id={saved_resource_id}")
            except Exception as e:
                logger.warning(f"[AgentService] 写入 evidence_links 失败: {e}")

        return {"code": 0, "message": "资源已保存到学习资源库", "data": {**saved, "db_resource_id": saved_resource_id}}

    def list_saved_resources(self, course_id: int = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        result = list_storage_files(course_id=course_id, page=page, page_size=page_size)
        return {"code": 0, "message": "success", "data": result}
