"""学习反馈 API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/learning", tags=["学习反馈"])

_MOCK_FEEDBACKS = [
    {
        "feedback_id": 1,
        "profile_id": 1,
        "student_name": "李明",
        "resource_id": 1,
        "resource_title": "SQL多表连接专题讲义",
        "course_id": 1,
        "course_name": "数据库系统原理",
        "feedback_type": "self_report",
        "content": "讲义内容清晰，案例丰富，但练习题偏少",
        "quiz_score": None,
        "self_mastery": 0.55,
        "difficulty_rating": "appropriate",
        "created_at": "2026-06-10T15:30:00"
    },
    {
        "feedback_id": 2,
        "profile_id": 1,
        "student_name": "李明",
        "resource_id": 2,
        "resource_title": "事务隔离级别测验",
        "course_id": 1,
        "course_name": "数据库系统原理",
        "feedback_type": "quiz_result",
        "content": "测验有一定难度，对隔离级别理解更深了",
        "quiz_score": 0.70,
        "self_mastery": None,
        "difficulty_rating": "appropriate",
        "created_at": "2026-06-09T10:00:00"
    },
    {
        "feedback_id": 3,
        "profile_id": 2,
        "student_name": "王悦",
        "resource_id": None,
        "resource_title": None,
        "course_id": 1,
        "course_name": "数据库系统原理",
        "feedback_type": "self_report",
        "content": "索引优化部分讲得很透彻",
        "quiz_score": None,
        "self_mastery": 0.68,
        "difficulty_rating": "too_easy",
        "created_at": "2026-06-08T14:20:00"
    }
]


@router.get("/feedbacks")
async def list_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    course_id: Optional[int] = None,
    feedback_type: Optional[str] = None,
    token: str = Depends(get_current_user),
):
    """获取学习反馈列表"""
    items = _MOCK_FEEDBACKS.copy()
    if course_id:
        items = [f for f in items if f["course_id"] == course_id]
    if feedback_type:
        items = [f for f in items if f["feedback_type"] == feedback_type]
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {"code": 0, "message": "success", "data": {"items": items[start:end], "total": total}}


@router.post("/feedbacks")
async def submit_feedback(
    data: dict,
    token: str = Depends(get_current_user),
):
    """提交学习反馈"""
    new_id = max(f["feedback_id"] for f in _MOCK_FEEDBACKS) + 1
    entry = {
        "feedback_id": new_id,
        "profile_id": 1,
        "student_name": "当前学生",
        "resource_id": data.get("resource_id"),
        "resource_title": None,
        "course_id": 1,
        "course_name": "数据库系统原理",
        "feedback_type": data.get("feedback_type", "self_report"),
        "content": data.get("content"),
        "quiz_score": data.get("quiz_score"),
        "self_mastery": data.get("self_mastery"),
        "difficulty_rating": data.get("difficulty_rating"),
        "created_at": "2026-06-11T20:00:00"
    }
    _MOCK_FEEDBACKS.insert(0, entry)
    return {"code": 0, "message": "反馈提交成功", "data": entry}
