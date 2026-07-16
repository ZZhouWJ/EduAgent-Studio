"""学习反馈 API"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.repositories.learning_feedback_repo import LearningFeedbackRepository
from app.repositories.profile_repo import ProfileRepository
from app.repositories.learning_resource_repo import LearningResourceRepository
from app.services.course_access_service import CourseAccessService
from app.services.learning_service import LearningService
from app.utils.dependencies import get_current_user_dep, require_role
from app.utils.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.utils.response import success_response

router = APIRouter(prefix="/learning", tags=["学习反馈"])
_repo = LearningFeedbackRepository()
_profile_repo = ProfileRepository()
_resource_repo = LearningResourceRepository()
_learning_service = LearningService()


class SubmitFeedbackRequest(BaseModel):
    course_id: Optional[int] = Field(None, gt=0)
    resource_id: Optional[int] = Field(None, gt=0)
    feedback_type: str = Field("self_report", min_length=1, max_length=50)
    content: Optional[str] = Field(None, max_length=4000)
    quiz_score: Optional[float] = Field(None, ge=0, le=1)
    self_mastery: Optional[float] = Field(None, ge=0, le=1)
    difficulty_rating: Optional[str] = Field(None, max_length=30)


@router.get("/feedbacks")
async def list_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    student_id: Optional[int] = Query(None, gt=0),
    feedback_type: Optional[str] = None,
    user: dict = Depends(get_current_user_dep),
):
    """获取学习反馈列表"""
    roles = set(user.get("roles") or [])
    is_teacher_or_admin = bool(roles.intersection({"teacher", "admin"}))
    effective_student_id = student_id
    if not is_teacher_or_admin:
        current_student_id = int(user["user_id"])
        if student_id is not None and student_id != current_student_id:
            raise ForbiddenException("无权查看其他学生的学习反馈")
        effective_student_id = current_student_id

    access = CourseAccessService()
    course_ids = access.list_accessible_course_ids(user)
    if course_id is not None:
        access.require_course_access(course_id, user)
    if is_teacher_or_admin and effective_student_id is not None:
        if course_id is None:
            raise ValidationException("按学生筛选时必须指定课程")
        access.require_student_course(course_id, effective_student_id)
    result = _repo.list_feedbacks(
        page=page,
        page_size=page_size,
        course_id=course_id,
        feedback_type=feedback_type,
        student_id=effective_student_id,
        course_ids=course_ids if course_id is None else None,
    )
    return success_response(data=result)


@router.post("/feedbacks")
async def submit_feedback(
    data: SubmitFeedbackRequest,
    user: dict = Depends(require_role("student_member")),
):
    """
    提交学习反馈，并自动更新知识点掌握度和学生画像。
    """
    user_id = int(user["user_id"])
    access = CourseAccessService()
    course_id = data.course_id
    resource = None
    if data.resource_id:
        resource_course_id = access.require_resource_access(data.resource_id, user)
        if course_id is not None and course_id != resource_course_id:
            raise ValidationException("反馈课程与学习资源课程不一致")
        course_id = resource_course_id
        resource = _resource_repo.get_resource(data.resource_id)

    if course_id is None:
        accessible_course_ids = access.list_accessible_course_ids(user) or []
        if len(accessible_course_ids) != 1:
            raise ValidationException("请先选择反馈所属课程")
        course_id = accessible_course_ids[0]
    else:
        access.require_course_access(course_id, user)

    profile_id = _profile_repo.get_profile_id_by_student_and_course(
        user_id, course_id
    )
    if profile_id is None:
        raise NotFoundException("未找到该课程的学生画像")

    entry = _repo.create_feedback(
        data=data.model_dump(),
        profile_id=profile_id,
        course_id=course_id,
        user_id=user_id,
    )

    target_kp_ids = (resource or {}).get("target_kp_ids") or []
    new_mastery = (
        data.quiz_score
        if data.quiz_score is not None
        else data.self_mastery
        if data.self_mastery is not None
        else None
    )

    mastery_changes: List[Dict[str, Any]] = []
    if new_mastery is not None and target_kp_ids:
        primary_kp_id = int(target_kp_ids[0])
        before_mastery = _profile_repo.get_mastery_level(profile_id, primary_kp_id)
        update_reason = (
            f"测验得分 {data.quiz_score * 100:.0f}%" if data.quiz_score is not None
            else f"自评掌握度 {data.self_mastery:.0%}" if data.self_mastery is not None
            else "学习反馈更新"
        )
        mastery = _profile_repo.update_mastery(
            profile_id,
            primary_kp_id,
            float(new_mastery),
            update_reason,
        )
        if mastery is not None:
            after_mastery = float(mastery["mastery_level"])
            before_value = before_mastery if before_mastery is not None else 0.0
            change = after_mastery - before_value
            mastery_changes.append({
                "kp_id": mastery["kp_id"],
                "kp_name": mastery.get("kp_name", ""),
                "before": round(before_value, 2),
                "after": round(after_mastery, 2),
                "change": f"{change:+.2f}",
            })

    # 构建扩展返回值
    response_data: Dict[str, Any] = {"feedback": entry}

    # 获取更新后的画像
    updated_profile = _profile_repo.get_profile(profile_id)
    if updated_profile:
        response_data["updated_profile"] = updated_profile

    # 获取 mastery 变化
    response_data["mastery_changes"] = mastery_changes

    # 获取下一步推荐资源
    next_resources = _learning_service.recommend_resources(profile_id, course_id)
    response_data["next_resources"] = next_resources

    # 学习路径调整
    path_adjustment: Dict[str, Any] = {"priority_change": "", "new_recommendations": []}
    if mastery_changes and next_resources:
        primary_change = mastery_changes[0] if mastery_changes else None
        if primary_change:
            kp_name = primary_change["kp_name"]
            if new_mastery is not None and new_mastery < 0.6:
                path_adjustment["priority_change"] = f"{kp_name}已提升为最优先"
                path_adjustment["new_recommendations"] = ["基础练习题", "案例分析"]
            elif new_mastery is not None and new_mastery >= 0.6:
                path_adjustment["priority_change"] = f"{kp_name}掌握良好，建议巩固练习"
                path_adjustment["new_recommendations"] = ["进阶练习题", "综合测验"]

    response_data["path_adjustment"] = path_adjustment

    return success_response(data=response_data, message="反馈提交成功，画像已更新")
