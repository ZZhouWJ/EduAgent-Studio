"""学习任务 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.auth_service import get_current_user_dependency as get_current_user

router = APIRouter(prefix="/learning", tags=["学习任务"])


@router.get("/tasks")
async def list_learning_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    token: str = Depends(get_current_user),
):
    """获取学习任务列表"""
    return {"code": 0, "message": "success", "data": {"items": [], "total": 0}}


@router.get("/courses")
async def list_courses(token: str = Depends(get_current_user)):
    """获取课程列表"""
    return {
        "code": 0,
        "message": "success",
        "data": [
            {"id": 1, "name": "数据库系统原理"},
            {"id": 2, "name": "Python程序设计"},
            {"id": 3, "name": "软件工程实践"}
        ]
    }
