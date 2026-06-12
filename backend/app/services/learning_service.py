"""学习服务 — 课程、知识点、学习任务"""

from typing import Any, Dict, Optional

from app.repositories import LearningRepository


class LearningService:
    """学习服务层，委托给 LearningRepository 执行数据库操作。"""

    def __init__(self) -> None:
        self._repo = LearningRepository()

    def list_courses(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": self._repo.list_courses()}

    def get_course(self, course_id: int) -> Dict[str, Any]:
        course = self._repo.get_course(course_id)
        if course is None:
            return {"code": 404, "message": "课程不存在", "data": None}
        return {"code": 0, "message": "success", "data": course}

    def list_tasks(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "code": 0,
            "message": "success",
            "data": self._repo.list_tasks(page=page, page_size=page_size, course_id=course_id, status=status),
        }

    def get_task(self, task_id: int) -> Dict[str, Any]:
        task = self._repo.get_task(task_id)
        if task is None:
            return {"code": 404, "message": "任务不存在", "data": None}
        return {"code": 0, "message": "success", "data": task}
