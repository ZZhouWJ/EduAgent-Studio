"""多智能体协作模块"""
from app.agents.diagnosis_agent import DiagnosisAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.resource_generation_agent import ResourceGenerationAgent
from app.agents.assessment_agent import AssessmentAgent
from app.agents.teacher_review_agent import TeacherReviewAgent
from app.agents.workflow import LearningAgentWorkflow

__all__ = [
    "DiagnosisAgent",
    "PlanningAgent",
    "ResourceGenerationAgent",
    "AssessmentAgent",
    "TeacherReviewAgent",
    "LearningAgentWorkflow",
]
