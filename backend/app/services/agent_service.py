"""智能体工作台 Service"""
from typing import Any, Dict, List
from app.agents.workflow import LearningAgentWorkflow
from app.llm.mock_provider import MockProvider
from app.llm.gateway import llm_gateway

llm_gateway.register_provider("mock", MockProvider())

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
    """智能体工作台 Service"""

    def __init__(self):
        self._workflow = LearningAgentWorkflow(llm_gateway)

    def list_agents(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": _MOCK_AGENTS}

    def generate(self, req: Any) -> Dict[str, Any]:
        """执行多智能体工作流"""
        from app.services.profile_service import ProfileService
        profile_service = ProfileService()

        student_profile = None
        for p in profile_service._MOCK_PROFILES:
            if p["student_id"] == req.student_id:
                student_profile = p
                break

        knowledge_points = _MOCK_KNOWLEDGE_POINTS.get(req.course_id, [])
        selected_kps = [kp for kp in knowledge_points if kp["id"] in req.knowledge_point_ids]

        result = self._workflow.run(
            student_id=req.student_id,
            course_id=req.course_id,
            knowledge_point_ids=req.knowledge_point_ids,
            resource_type=req.resource_type,
            difficulty=req.difficulty,
            student_profile=student_profile,
            knowledge_points=selected_kps,
        )

        return {"code": 0, "message": "success", "data": result}

    def save_resource(self, req: Any) -> Dict[str, Any]:
        """保存学习资源"""
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
