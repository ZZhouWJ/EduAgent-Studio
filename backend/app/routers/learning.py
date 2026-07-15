"""学习任务 API — 课程、知识点、学习任务、学习路径"""
from typing import Any, Optional

from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, Field

from app.services import learning_service
from app.services.course_access_service import CourseAccessService
from app.services.profile_service import ProfileService
from app.utils.dependencies import get_current_user_dep, require_role

router = APIRouter(prefix="/learning", tags=["学习任务"])


class CreateLearningTaskRequest(BaseModel):
    course_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    target_kp_ids: Optional[list[int]] = Field(None)
    assignee_id: Optional[int] = Field(None)
    due_date: Optional[str] = Field(None)  # "YYYY-MM-DD" 格式


class UpdateCourseStatusRequest(BaseModel):
    status: str = Field(..., description="课程状态: active / archived / draft")


@router.get("/courses")
async def list_courses(user: dict = Depends(get_current_user_dep)):
    """获取课程列表（包含知识点摘要）"""
    return learning_service.LearningService().list_courses(user)


@router.get("/courses/{course_id}")
async def get_course(
    course_id: int = Path(..., gt=0),
    user: dict = Depends(get_current_user_dep),
):
    """获取课程详情（含知识点列表）"""
    CourseAccessService().require_course_access(course_id, user)
    return learning_service.LearningService().get_course(course_id)


@router.put("/courses/{course_id}")
async def update_course(
    course_id: int = Path(..., gt=0),
    body: UpdateCourseStatusRequest = ...,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """更新课程状态"""
    CourseAccessService().require_course_access(course_id, user)
    return learning_service.LearningService().update_course_status(course_id, body.status)


@router.get("/tasks")
async def list_learning_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    status: Optional[str] = None,
    user: dict = Depends(get_current_user_dep),
):
    """获取学习任务列表（分页、课程过滤、状态过滤）"""
    return learning_service.LearningService().list_tasks(
        user=user,
        page=page,
        page_size=page_size,
        course_id=course_id,
        status=status,
    )


@router.get("/tasks/{task_id}")
async def get_learning_task(
    task_id: int = Path(..., gt=0),
    user: dict = Depends(get_current_user_dep),
):
    """获取学习任务详情"""
    CourseAccessService().require_task_access(task_id, user)
    return learning_service.LearningService().get_task(task_id)


@router.post("/tasks")
async def create_learning_task(
    body: CreateLearningTaskRequest,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """创建学习任务"""
    CourseAccessService().require_course_access(body.course_id, user)
    return learning_service.LearningService().create_task(
        course_id=body.course_id,
        title=body.title,
        description=body.description,
        target_kp_ids=body.target_kp_ids,
        assignee_id=body.assignee_id,
        due_date=body.due_date,
        creator_id=int(user["user_id"]),
    )


# =============================================================================
# 学习路径图谱
# =============================================================================

@router.get("/courses/{course_id}/learning-path")
async def get_learning_path(
    course_id: int = Path(..., gt=0),
    profile_id: Optional[int] = None,
    user: dict = Depends(get_current_user_dep),
):
    """
    获取课程知识点学习路径图谱。

    - 包含知识点依赖关系（parent_kp_id）
    - 包含学生掌握度数据（若传入 profile_id）
    - 适合用 ECharts graph 渲染

    Returns:
        { nodes: [...], edges: [...], summary: {...} }
    """
    access_service = CourseAccessService()
    if profile_id is not None:
        ProfileService().require_profile_access(profile_id, user)
        access_service.require_profile_course(profile_id, course_id, user)
    else:
        access_service.require_course_access(course_id, user)
    return learning_service.LearningService().get_learning_path(course_id, profile_id)


@router.get("/recommend")
async def get_recommended_resources(
    profile_id: int = Query(..., gt=0),
    course_id: int = Query(..., gt=0),
    user: dict = Depends(get_current_user_dep),
):
    """
    根据学生画像推荐学习资源。

    - 低 mastery 知识点优先
    - 匹配学生资源偏好
    - 未学习过的资源
    - 教师审核通过资源
    """
    ProfileService().require_profile_access(profile_id, user)
    CourseAccessService().require_profile_course(profile_id, course_id, user)
    service = learning_service.LearningService()
    resources = service.recommend_resources(profile_id, course_id)
    return {"code": 0, "message": "success", "data": resources}
