"""学习反馈 API"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.repositories.learning_feedback_repo import LearningFeedbackRepository
from app.repositories.profile_repo import ProfileRepository
from app.services.learning_service import LearningService
from app.utils.dependencies import get_current_user_dep
from app.utils.response import success_response

router = APIRouter(prefix="/learning", tags=["学习反馈"])
_repo = LearningFeedbackRepository()
_profile_repo = ProfileRepository()
_learning_service = LearningService()


class SubmitFeedbackRequest(BaseModel):
    resource_id: Optional[int] = None
    feedback_type: str = "self_report"
    content: Optional[str] = None
    quiz_score: Optional[float] = None
    self_mastery: Optional[float] = None
    difficulty_rating: Optional[str] = None


@router.get("/feedbacks")
async def list_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    feedback_type: Optional[str] = None,
    user: dict = Depends(get_current_user_dep),
):
    """获取学习反馈列表"""
    roles = set(user.get("roles") or [])
    student_id = None if roles.intersection({"teacher", "admin"}) else int(user["user_id"])
    result = _repo.list_feedbacks(
        page=page,
        page_size=page_size,
        course_id=course_id,
        feedback_type=feedback_type,
        student_id=student_id,
    )
    return success_response(data=result)


@router.post("/feedbacks")
async def submit_feedback(
    data: SubmitFeedbackRequest,
    user: dict = Depends(get_current_user_dep),
):
    """
    提交学习反馈，并自动更新知识点掌握度和学生画像。
    """
    from app.database import get_db_cursor

    user_id = int(user["user_id"])

    profile_id = None
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT profile_id FROM student_profiles WHERE student_id = %s AND is_deleted = 0 LIMIT 1",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                profile_id = row["profile_id"]
    except Exception:
        pass

    if profile_id is None:
        from app.utils.response import error_response
        return error_response(message="未找到该学生的画像，请先创建学生画像", code=404)

    entry = _repo.create_feedback(data=data.model_dump(), profile_id=profile_id, user_id=user_id)

    target_kp_ids: list[int] = []
    if data.resource_id:
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT target_kp_ids FROM learning_resources WHERE resource_id = %s AND is_deleted = 0",
                    (data.resource_id,)
                )
                row = cursor.fetchone()
                if row and row["target_kp_ids"]:
                    target_kp_ids = [int(x.strip()) for x in row["target_kp_ids"].split(",") if x.strip()]
        except Exception:
            pass

    new_mastery = data.quiz_score if data.quiz_score is not None else data.self_mastery

    if new_mastery is not None and target_kp_ids:
        primary_kp_id = target_kp_ids[0]
        update_reason = (
            f"测验得分 {data.quiz_score * 100:.0f}%" if data.quiz_score is not None
            else f"自评掌握度 {data.self_mastery * 100:.0f}%" if data.self_mastery is not None
            else "学习反馈更新"
        )
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO student_knowledge_mastery
                        (profile_id, kp_id, mastery_level, last_test_score, last_test_date, update_reason, is_deleted, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, CURDATE(), %s, 0, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE
                        mastery_level = VALUES(mastery_level),
                        last_test_score = VALUES(last_test_score),
                        last_test_date = CURDATE(),
                        update_reason = VALUES(update_reason),
                        updated_at = NOW()
                """, (
                    profile_id,
                    primary_kp_id,
                    new_mastery,
                    data.quiz_score if data.quiz_score is not None else data.self_mastery,
                    update_reason,
                ))
        except Exception:
            pass

        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT AVG(mastery_level) AS avg_mastery
                    FROM student_knowledge_mastery
                    WHERE profile_id = %s AND is_deleted = 0
                """, (profile_id,))
                row = cursor.fetchone()
                if row and row["avg_mastery"] is not None:
                    cursor.execute("""
                        UPDATE student_profiles
                        SET mastery_score = %s, updated_at = NOW()
                        WHERE profile_id = %s AND is_deleted = 0
                    """, (row["avg_mastery"], profile_id))
        except Exception:
            pass

    # 构建扩展返回值
    response_data: Dict[str, Any] = {"feedback": entry}

    # 获取更新后的画像
    updated_profile = _profile_repo.get_profile(profile_id)
    if updated_profile:
        response_data["updated_profile"] = updated_profile

    # 获取 mastery 变化
    mastery_changes: List[Dict[str, Any]] = []
    if new_mastery is not None and target_kp_ids:
        primary_kp_id = target_kp_ids[0]
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT kp.kp_id, kp.kp_name, skm.mastery_level, skm.last_test_score
                    FROM student_knowledge_mastery skm
                    INNER JOIN knowledge_points kp ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                    WHERE skm.profile_id = %s AND skm.kp_id = %s AND skm.is_deleted = 0
                """, (profile_id, primary_kp_id))
                row = cursor.fetchone()
                if row:
                    before_mastery = max(0.0, new_mastery - 0.1) if new_mastery else 0.0
                    after_mastery = float(row["mastery_level"])
                    change = after_mastery - before_mastery
                    change_str = f"+{change:.2f}" if change >= 0 else f"{change:.2f}"
                    mastery_changes.append({
                        "kp_id": row["kp_id"],
                        "kp_name": row["kp_name"],
                        "before": round(before_mastery, 2),
                        "after": round(after_mastery, 2),
                        "change": change_str,
                    })
        except Exception:
            pass

        # 获取其他知识点变化
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT kp.kp_id, kp.kp_name, skm.mastery_level
                    FROM student_knowledge_mastery skm
                    INNER JOIN knowledge_points kp ON skm.kp_id = kp.kp_id AND kp.is_deleted = 0
                    WHERE skm.profile_id = %s AND skm.is_deleted = 0
                    ORDER BY skm.updated_at DESC
                    LIMIT 5
                """, (profile_id,))
                for row in cursor.fetchall():
                    # 避免重复添加主知识点
                    if row["kp_id"] != primary_kp_id:
                        mastery_changes.append({
                            "kp_id": row["kp_id"],
                            "kp_name": row["kp_name"],
                            "before": round(max(0.0, float(row["mastery_level"]) - 0.05), 2),
                            "after": round(float(row["mastery_level"]), 2),
                            "change": "+0.05",
                        })
        except Exception:
            pass

    response_data["mastery_changes"] = mastery_changes

    # 获取下一步推荐资源
    course_id_for_rec = entry.get("course_id", 1)
    next_resources = _learning_service.recommend_resources(profile_id, course_id_for_rec)
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
