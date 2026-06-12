<<<<<<< HEAD
"""学习任务 API — 课程、知识点、学习任务、学习路径"""
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query

from app.services.auth_service import get_current_user_dependency as get_current_user
from app.services import learning_service
=======
"""学习任务 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.auth_service import get_current_user
>>>>>>> origin/main

router = APIRouter(prefix="/learning", tags=["学习任务"])


<<<<<<< HEAD
@router.get("/courses")
async def list_courses(token: str = Depends(get_current_user)):
    """获取课程列表（包含知识点摘要）"""
    return learning_service.LearningService().list_courses()


@router.get("/courses/{course_id}")
async def get_course(
    course_id: int = Path(..., gt=0),
    token: str = Depends(get_current_user),
):
    """获取课程详情（含知识点列表）"""
    return learning_service.LearningService().get_course(course_id)


=======
>>>>>>> origin/main
@router.get("/tasks")
async def list_learning_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
<<<<<<< HEAD
    status: Optional[str] = None,
    token: str = Depends(get_current_user),
):
    """获取学习任务列表（分页、课程过滤、状态过滤）"""
    return learning_service.LearningService().list_tasks(
        page=page, page_size=page_size, course_id=course_id, status=status
    )


@router.get("/tasks/{task_id}")
async def get_learning_task(
    task_id: int = Path(..., gt=0),
    token: str = Depends(get_current_user),
):
    """获取学习任务详情"""
    return learning_service.LearningService().get_task(task_id)


# =============================================================================
# 学习路径图谱
# =============================================================================

@router.get("/courses/{course_id}/learning-path")
async def get_learning_path(
    course_id: int = Path(..., gt=0),
    profile_id: Optional[int] = None,
    token: str = Depends(get_current_user),
):
    """
    获取课程知识点学习路径图谱。

    - 包含知识点依赖关系（parent_kp_id）
    - 包含学生掌握度数据（若传入 profile_id）
    - 适合用 ECharts graph 渲染

    Returns:
        { nodes: [...], edges: [...], summary: {...} }
    """
    return learning_service.LearningService().get_learning_path(course_id, profile_id)
=======
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
>>>>>>> origin/main
