"""智能体工作台 Service — LangGraph 标准版"""
import os
from datetime import datetime
from typing import Any, Dict, List

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

_MOCK_AGENTS = [
    {"id": "diagnosis_agent", "name": "学习诊断智能体", "description": "分析学生薄弱知识点", "type": "diagnosis"},
    {"id": "planning_agent", "name": "资源规划智能体", "description": "生成个性化学习路径", "type": "planning"},
    {"id": "resource_generation_agent", "name": "资源生成智能体", "description": "生成学习资源", "type": "generation"},
    {"id": "assessment_agent", "name": "评测反馈智能体", "description": "分析学习效果", "type": "assessment"},
    {"id": "teacher_review_agent", "name": "教师审核辅助智能体", "description": "生成资源质量建议", "type": "review"},
]

_MOCK_KNOWLEDGE_POINTS = {
    1: [
        {"id": 1, "name": "关系模型基础", "mastery_level": 0.75},
        {"id": 2, "name": "SQL基本查询", "mastery_level": 0.85},
        {"id": 3, "name": "数据定义DDL", "mastery_level": 0.78},
        {"id": 5, "name": "SQL多表连接", "mastery_level": 0.30},
        {"id": 8, "name": "事务隔离级别", "mastery_level": 0.20},
        {"id": 12, "name": "数据库范式", "mastery_level": 0.40},
    ],
    2: [
        {"id": 20, "name": "Python基础语法", "mastery_level": 0.72},
        {"id": 21, "name": "函数参数传递", "mastery_level": 0.45},
        {"id": 22, "name": "模块导入", "mastery_level": 0.38},
        {"id": 23, "name": "异常处理", "mastery_level": 0.42},
    ],
    3: [
        {"id": 30, "name": "需求分析", "mastery_level": 0.60},
        {"id": 31, "name": "UML建模", "mastery_level": 0.55},
    ]
}


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
        return {"code": 0, "message": "success", "data": _MOCK_AGENTS}

    def generate(self, req: Any, checkpoint_id: str = None) -> Dict[str, Any]:
        """执行多智能体工作流（LangGraph 标准版）"""
        from app.services.profile_service import _MOCK_PROFILES as _PROFILES

        student_profile = None
        for p in _PROFILES:
            if p["student_id"] == req.student_id:
                student_profile = p
                break

        knowledge_points = _MOCK_KNOWLEDGE_POINTS.get(req.course_id, [])
        selected_kps = [kp for kp in knowledge_points if kp["id"] in req.knowledge_point_ids]

        raw = run_workflow(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            student_profile=student_profile,
            knowledge_points=selected_kps,
            learning_history=None,
            run_id=None,
            checkpoint_id=checkpoint_id,
        )

        return {"code": 0, "message": "success", "data": _map_workflow_result(raw)}

    def generate_stream(self, req: Any):
        """流式执行工作流，yield 每个步骤的中间结果（SSE 推送）"""
        from app.services.profile_service import _MOCK_PROFILES as _PROFILES

        student_profile = None
        for p in _PROFILES:
            if p["student_id"] == req.student_id:
                student_profile = p
                break

        knowledge_points = _MOCK_KNOWLEDGE_POINTS.get(req.course_id, [])
        selected_kps = [kp for kp in knowledge_points if kp["id"] in req.knowledge_point_ids]

        return stream_workflow(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            student_profile=student_profile,
            knowledge_points=selected_kps,
            learning_history=None,
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
