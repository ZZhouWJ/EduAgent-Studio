"""学习资源 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.auth_service import get_current_user_dependency as get_current_user

router = APIRouter(prefix="/learning", tags=["学习资源"])

_MOCK_RESOURCES = [
    {
        "resource_id": 1,
        "course_id": 1,
        "course_name": "数据库系统原理",
        "resource_title": "SQL多表连接专题讲义（进阶）",
        "resource_type": "lecture",
        "difficulty": "intermediate",
        "status": "pending_review",
        "created_at": "2026-06-10T15:00:00"
    },
    {
        "resource_id": 2,
        "course_id": 1,
        "course_name": "数据库系统原理",
        "resource_title": "数据库范式复习计划",
        "resource_type": "review",
        "difficulty": "intermediate",
        "status": "approved",
        "created_at": "2026-06-09T10:00:00"
    },
    {
        "resource_id": 3,
        "course_id": 2,
        "course_name": "Python程序设计",
        "resource_title": "函数与模块练习题",
        "resource_type": "quiz",
        "difficulty": "basic",
        "status": "approved",
        "created_at": "2026-06-08T14:00:00"
    }
]


@router.get("/resources")
async def list_resources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    type: Optional[str] = None,
    token: str = Depends(get_current_user),
):
    items = _MOCK_RESOURCES.copy()
    if course_id:
        items = [r for r in items if r["course_id"] == course_id]
    if type:
        items = [r for r in items if r["resource_type"] == type]
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {"code": 0, "message": "success", "data": {"items": items[start:end], "total": total}}


@router.get("/resources/{resource_id}")
async def get_resource(
    resource_id: int,
    token: str = Depends(get_current_user),
):
    for r in _MOCK_RESOURCES:
        if r["resource_id"] == resource_id:
            return {"code": 0, "message": "success", "data": r}
    return {"code": 404, "message": "资源不存在", "data": None}
