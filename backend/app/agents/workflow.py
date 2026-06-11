"""
多智能体工作流编排

编排 5 个智能体的协作链路：诊断 → 规划 → 生成 → 评测 → 审核建议
"""
import logging
from typing import Any, Dict, List, Optional

from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.resource_generation_agent import ResourceGenerationAgent
from app.agents.assessment_agent import AssessmentAgent
from app.agents.teacher_review_agent import TeacherReviewAgent

logger = logging.getLogger(__name__)


class LearningAgentWorkflow:
    """多智能体工作流"""

    def __init__(self, llm_gateway=None):
        self.diagnosis_agent = DiagnosisAgent(llm_gateway)
        self.planning_agent = PlanningAgent(llm_gateway)
        self.resource_agent = ResourceGenerationAgent(llm_gateway)
        self.assessment_agent = AssessmentAgent()
        self.review_agent = TeacherReviewAgent()

    def run(
        self,
        student_id: int,
        course_id: int,
        knowledge_point_ids: List[int],
        resource_type: str,
        difficulty: str,
        student_profile: Optional[Dict[str, Any]] = None,
        knowledge_points: Optional[List[Dict[str, Any]]] = None,
        learning_history: Optional[List[Dict[str, Any]]] = None,
        test_results: Optional[Dict[str, Any]] = None,
        learning_feedback: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行完整的多智能体工作流。
        """
        state: Dict[str, Any] = {
            "student_id": student_id,
            "course_id": course_id,
            "knowledge_point_ids": knowledge_point_ids,
            "resource_type": resource_type,
            "difficulty": difficulty,
            "diagnosis": None,
            "learning_plan": None,
            "generated_resource": None,
            "assessment": None,
            "teacher_review_suggestion": None,
            "current_step": "idle",
            "messages": [],
            "error": None,
        }

        # 步骤 1: 学习诊断
        state["current_step"] = "diagnosis"
        state["messages"].append("开始执行学习诊断...")
        try:
            state["diagnosis"] = self.diagnosis_agent.run(
                student_profile=student_profile or {},
                knowledge_points=knowledge_points or [],
                learning_history=learning_history or [],
            )
            state["messages"].append("诊断完成：识别薄弱知识点")
        except Exception as e:
            logger.error(f"Diagnosis agent failed: {e}")
            state["error"] = f"诊断失败: {str(e)}"

        # 步骤 2: 资源规划
        state["current_step"] = "planning"
        state["messages"].append("开始生成学习路径...")
        try:
            state["learning_plan"] = self.planning_agent.run(
                diagnosis=state["diagnosis"],
                learning_goal=student_profile.get("learning_goal", "") if student_profile else "",
                course_outline=knowledge_points or [],
            )
            state["messages"].append("规划完成：生成学习路径")
        except Exception as e:
            logger.error(f"Planning agent failed: {e}")
            state["error"] = f"规划失败: {str(e)}"

        # 步骤 3: 资源生成
        state["current_step"] = "generation"
        state["messages"].append("开始生成学习资源...")
        try:
            state["generated_resource"] = self.resource_agent.run(
                learning_path=state["learning_plan"].get("learning_path", []) if state["learning_plan"] else [],
                resource_type=resource_type,
                difficulty=difficulty,
                student_profile=student_profile or {},
            )
            state["messages"].append(f"生成完成：{state['generated_resource'].get('title', '学习资源')}")
        except Exception as e:
            logger.error(f"Resource generation agent failed: {e}")
            state["error"] = f"生成失败: {str(e)}"

        # 步骤 4: 评测反馈
        state["current_step"] = "assessment"
        state["messages"].append("开始生成评测反馈...")
        try:
            state["assessment"] = self.assessment_agent.run(
                test_results=test_results,
                learning_feedback=learning_feedback,
                generated_resource=state["generated_resource"],
                student_profile=student_profile,
            )
            state["messages"].append("评测完成：生成改进建议")
        except Exception as e:
            logger.error(f"Assessment agent failed: {e}")

        # 步骤 5: 教师审核辅助
        state["current_step"] = "teacher_review"
        state["messages"].append("开始生成审核建议...")
        try:
            state["teacher_review_suggestion"] = self.review_agent.run(
                generated_resource=state["generated_resource"],
                difficulty_requirement=difficulty,
            )
            state["messages"].append("审核建议生成完成")
        except Exception as e:
            logger.error(f"Teacher review agent failed: {e}")

        state["current_step"] = "completed"
        state["messages"].append("全部智能体执行完成")
        logger.info(f"[Workflow] 完成，学生ID={student_id}，资源={state['generated_resource'].get('title') if state['generated_resource'] else 'N/A'}")

        return {
            "diagnosis": state["diagnosis"],
            "plan": state["learning_plan"],
            "resource": state["generated_resource"],
            "assessment": state["assessment"],
            "teacher_review_suggestion": state["teacher_review_suggestion"],
            "metadata": {
                "current_step": state["current_step"],
                "messages": state["messages"],
                "error": state["error"],
            }
        }
