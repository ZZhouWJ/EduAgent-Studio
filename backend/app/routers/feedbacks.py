"""学习反馈 API"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.repositories.learning_feedback_repo import LearningFeedbackRepository
from app.services.auth_service import get_current_user_dependency as get_current_user
from app.utils.response import success_response

router = APIRouter(prefix="/learning", tags=["学习反馈"])
_repo = LearningFeedbackRepository()


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
    token: str = Depends(get_current_user),
):
    """获取学习反馈列表"""
    result = _repo.list_feedbacks(
        page=page,
        page_size=page_size,
        course_id=course_id,
        feedback_type=feedback_type,
    )
    return success_response(data=result)


@router.post("/feedbacks")
async def submit_feedback(
    data: SubmitFeedbackRequest,
    token: str = Depends(get_current_user),
):
    """
    提交学习反馈，并自动更新知识点掌握度和学生画像。

    规则：
    - 如果有 quiz_score → 用它更新知识点掌握度
    - 如果有 self_mastery → 用它更新
    - 取 resource_id 关联的 target_kp_ids 中第一个作为本次学习知识点
    """
    from app.services.auth_service import get_current_user as get_user
    from app.database import get_db_cursor

    user = get_user(token)
    user_id = user.get("user_id", 0) if user else 0

    # 获取用户的 profile_id
    profile_id = 1
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

    entry = _repo.create_feedback(data=data.model_dump(), profile_id=profile_id, user_id=user_id)

    # === 画像更新闭环 ===
    # 1. 解析本次学习的知识点 ID
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

    # 2. 确定新掌握度
    new_mastery = data.quiz_score if data.quiz_score is not None else data.self_mastery

    # 3. 更新 / 插入知识点掌握度
    if new_mastery is not None and target_kp_ids:
        primary_kp_id = target_kp_ids[0]
        update_reason = (
            f"测验得分 {data.quiz_score * 100:.0f}%" if data.quiz_score is not None
            else f"自评掌握度 {data.self_mastery * 100:.0f}%" if data.self_mastery is not None
            else "学习反馈更新"
        )
        try:
            with get_db_cursor() as cursor:
                # UPSERT：存在则更新，不存在则插入
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

        # 4. 重算综合掌握度 AVG(all_kp_mastery)
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

    return success_response(data=entry, message="反馈提交成功，画像已更新")
