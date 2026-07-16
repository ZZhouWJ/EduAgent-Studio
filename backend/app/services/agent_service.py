"""智能体工作台 Service — LangGraph 标准版"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

from app.config import get_settings
from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.minimax_provider import MiniMaxProvider
from app.llm.iflytek_provider import IFlyTekProvider
from app.llm.gateway import llm_gateway
from app.database import get_db_transaction
from app.utils.exceptions import NotFoundException, ValidationException

settings = get_settings()

_llm_registered = False
if not _llm_registered:
    llm_gateway.register_provider("mock", MockProvider())
    openai_compatible_provider = OpenAICompatibleProvider(
        model_name=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )
    for provider_code in ("openai_compatible", "openai", "deepseek", "qwen"):
        llm_gateway.register_provider(provider_code, openai_compatible_provider)
    llm_gateway.register_provider("minimax", MiniMaxProvider(
        model_name=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    ))
    # 讯飞星火（当 LLM_PROVIDER=iflytek 时由 gateway 路由至此）
    if all((settings.iflytek_app_id, settings.iflytek_api_key, settings.iflytek_api_secret)):
        llm_gateway.register_provider("iflytek", IFlyTekProvider(
            model_name=settings.llm_model,        # 星火 domain，如 "general"
            api_key=settings.iflytek_api_key,
            api_secret=settings.iflytek_api_secret,
            app_id=settings.iflytek_app_id,
        ))
        logger.info("[IFlyTek] Provider registered for model=%s", settings.llm_model)
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


def _extract_save_payload(result: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize synchronous and streamed workflow results before persistence."""
    raw = result.get("_raw") or {}
    if not isinstance(raw, dict):
        raw = {}

    resource = raw.get("generated_resource") or result.get("resource") or {}
    metadata = result.get("metadata") or {}
    evidence_links = raw.get("evidence_links")
    if evidence_links is None:
        evidence_links = result.get("evidence_links") or []

    return {
        "resource": resource,
        "evidence_links": evidence_links,
        "trustworthiness": raw.get(
            "trustworthiness", result.get("trustworthiness", "draft")
        ),
        "quality_score": raw.get(
            "quality_score", metadata.get("quality_score")
        ),
        "step_history": raw.get(
            "step_history", metadata.get("step_history", [])
        ),
    }


def extract_resource_references(result: Dict[str, Any]) -> Dict[str, List[int]]:
    payload = _extract_save_payload(result)
    resource = payload["resource"]
    raw_kp_ids = resource.get("target_kp_ids") or resource.get("knowledge_points") or []
    if isinstance(raw_kp_ids, str):
        raw_kp_ids = [value.strip() for value in raw_kp_ids.split(",") if value.strip()]
    if not isinstance(raw_kp_ids, list):
        raise ValidationException("资源知识点引用格式错误")

    evidence_links = payload["evidence_links"]
    if not isinstance(evidence_links, list) or any(
        not isinstance(link, dict) or link.get("chunk_id") is None
        for link in evidence_links
    ):
        raise ValidationException("资源证据引用格式错误")

    try:
        kp_ids = [int(value) for value in raw_kp_ids]
        chunk_ids = [int(link["chunk_id"]) for link in evidence_links]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationException("资源引用包含无效 ID") from exc
    if any(value <= 0 for value in [*kp_ids, *chunk_ids]):
        raise ValidationException("资源引用包含无效 ID")
    return {
        "kp_ids": list(dict.fromkeys(kp_ids)),
        "chunk_ids": list(dict.fromkeys(chunk_ids)),
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

    def _load_learning_history(
        self, student_id: int, course_id: int
    ) -> List[Dict[str, Any]]:
        try:
            from app.repositories.learning_feedback_repo import LearningFeedbackRepository
            repo = LearningFeedbackRepository()
            result = repo.list_feedbacks(
                page=1,
                page_size=10,
                course_id=course_id,
                student_id=student_id,
            )
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

    def _resolve_profile(self, student_id: int, course_id: int):
        from app.repositories.profile_repo import ProfileRepository

        profile = ProfileRepository().get_profile_by_student_and_course(
            student_id, course_id
        )
        if not profile:
            raise NotFoundException("该课程中不存在此学生画像")
        return profile.get("profile_id"), profile

    def generate(self, req: Any, checkpoint_id: str = None) -> Dict[str, Any]:
        profile_id, student_profile = self._resolve_profile(
            req.student_id, req.course_id
        )
        selected_kps = self._load_knowledge_points(req.course_id, req.knowledge_point_ids, profile_id)
        learning_history = self._load_learning_history(req.student_id, req.course_id)

        raw = run_workflow(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            generation_goal=req.generation_goal,
            student_profile=student_profile,
            knowledge_points=selected_kps,
            learning_history=learning_history,
            run_id=None,
            checkpoint_id=checkpoint_id,
        )

        return {"code": 0, "message": "success", "data": _map_workflow_result(raw)}

    def generate_stream(self, req: Any):
        profile_id, student_profile = self._resolve_profile(
            req.student_id, req.course_id
        )
        selected_kps = self._load_knowledge_points(req.course_id, req.knowledge_point_ids, profile_id)
        learning_history = self._load_learning_history(req.student_id, req.course_id)

        return stream_workflow(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            generation_goal=req.generation_goal,
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
        from app.repositories import user_repo
        from app.repositories.evidence_repo import EvidenceRepository
        from app.repositories.learning_resource_repo import LearningResourceRepository

        payload = _extract_save_payload(req.result)
        references = extract_resource_references(req.result)
        resource = payload["resource"]
        evidence_links = payload["evidence_links"]
        trustworthiness = payload["trustworthiness"]

        title = (req.title or resource.get("title") or "").strip()
        content = str(resource.get("content") or "").strip()
        if not title:
            raise ValidationException("资源标题不能为空")
        if not content:
            raise ValidationException("资源内容不能为空")

        lr_repo = LearningResourceRepository()
        with get_db_transaction() as conn:
            created = lr_repo.create_resource(
                data={
                    "course_id": req.course_id,
                    "resource_title": title,
                    "resource_type": resource.get("type", "lecture"),
                    "difficulty": resource.get("difficulty", "intermediate"),
                    "content": content,
                    "target_kp_ids": references["kp_ids"],
                    "generation_model": resource.get("generation_metadata", {}).get("model"),
                    "generation_agent": resource.get("generation_metadata", {}).get("agent"),
                    "status": "draft",
                },
                created_by=user_id,
                conn=conn,
            )
            resource_id = int(created["resource_id"])
            if evidence_links:
                EvidenceRepository().insert_resource_evidence_links(
                    [{**link, "resource_id": resource_id} for link in evidence_links],
                    conn=conn,
                )
            user_repo.insert_operation_log_with_conn(
                user_id=user_id,
                action_type="learning_resource:create",
                action_desc=f"保存智能体生成资源草稿: {title}",
                target_type="learning_resource",
                target_id=resource_id,
                conn=conn,
            )

        saved = lr_repo.get_resource(resource_id)
        if saved is None:
            raise NotFoundException("资源保存后无法读取")
        return {
            "code": 0,
            "message": "资源草稿已保存",
            "data": {
                **saved,
                "evidence_count": len(evidence_links),
                "trustworthiness": trustworthiness,
                "quality_score": payload["quality_score"],
            },
        }
