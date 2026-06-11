"""智能体工作台 API"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.services.agent_service import AgentService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/agents", tags=["智能体工作台"])


class GenerateRequest(BaseModel):
    student_id: int
    course_id: int
    knowledge_point_ids: list[int]
    resource_type: str
    difficulty: str


class SaveResourceRequest(BaseModel):
    result: dict
    title: str
    course_id: int


@router.get("/list")
async def list_agents(token: str = Depends(get_current_user)):
    """获取智能体列表"""
    service = AgentService()
    return service.list_agents()


@router.post("/generate")
async def generate_learning_resource(
    req: GenerateRequest,
    token: str = Depends(get_current_user),
):
    """执行多智能体协作，生成个性化学习资源"""
    service = AgentService()
    return service.generate(req)


@router.post("/save-resource")
async def save_resource(
    req: SaveResourceRequest,
    token: str = Depends(get_current_user),
):
    """保存生成的学习资源"""
    service = AgentService()
    return service.save_resource(req)
