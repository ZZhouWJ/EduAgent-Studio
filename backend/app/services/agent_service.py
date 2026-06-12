"""智能体工作台 Service — LangGraph 标准版"""
from typing import Any, Dict, List

from app.llm.mock_provider import MockProvider
from app.llm.openai_compatible_provider import OpenAICompatibleProvider
from app.llm.gateway import llm_gateway
from app.config import get_settings

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
    _llm_registered = True

# LangGraph 工作流在 workflow 模块内按需构建，这里只做参数组装和调用
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

_SAVED_RESOURCES = []


class AgentService:
    """智能体工作台 Service — LangGraph 驱动"""

    def list_agents(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": _MOCK_AGENTS}

    def generate(self, req: Any, checkpoint_id: str = None) -> Dict[str, Any]:
        """
        执行多智能体工作流（LangGraph 标准版）。

        Args:
            req: GenerateRequest 对象
            checkpoint_id: 可选，从断点恢复时传入 thread_id

        流程：
        1. 补全学生画像和知识点数据
        2. 调用 LangGraph run_workflow（自动 Supervisor 路由）
        3. 返回完整状态（含所有 Agent 输出 + 步骤历史 + 质量评分）
        """
        from app.services.profile_service import _MOCK_PROFILES as _PROFILES

        # 补全学生画像
        student_profile = None
        for p in _PROFILES:
            if p["student_id"] == req.student_id:
                student_profile = p
                break

        # 补全知识点数据
        knowledge_points = _MOCK_KNOWLEDGE_POINTS.get(req.course_id, [])
        selected_kps = [kp for kp in knowledge_points if kp["id"] in req.knowledge_point_ids]

        # 执行 LangGraph 工作流
        result = run_workflow(
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

        return {"code": 0, "message": "success", "data": result}

    def generate_stream(self, req: Any):
        """
        流式执行工作流，yield 每个步骤的中间结果。

        用于 SSE/长连接推送，前端可实时显示每个 Agent 的执行状态。
        """
        from app.services.profile_service import _MOCK_PROFILES as _PROFILES
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
        """
        查询某个工作流运行的状态（从 Checkpoint 恢复）。

        用于断点续传场景，前端可以查看之前暂停的工作流进度。
        """
        graph = get_compiled_graph()
        config = {"configurable": {"thread_id": run_id}}
        state = graph.get_state(config)
        if state and state.values:
            return {"code": 0, "message": "success", "data": state.values}
        return {"code": 404, "message": "未找到运行记录", "data": None}

    def save_resource(self, req: Any) -> Dict[str, Any]:
        """保存学习资源到本地资源库"""
        resource = req.result.get("resource", {})
        saved = {
            "resource_id": resource.get("resource_id"),
            "title": req.title or resource.get("title"),
            "course_id": req.course_id,
            "type": resource.get("type"),
            "content": resource.get("content"),
            "knowledge_points": resource.get("knowledge_points", []),
            "difficulty": resource.get("difficulty"),
            "status": "pending_review",
        }
        _SAVED_RESOURCES.append(saved)
        return {"code": 0, "message": "资源已保存到学习资源库", "data": saved}
