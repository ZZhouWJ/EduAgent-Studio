"""学习服务 — 课程、知识点、学习任务"""

from typing import Any, Dict, List, Optional

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

    def update_course_status(self, course_id: int, status: str) -> Dict[str, Any]:
        try:
            result = self._repo.update_course_status(course_id, status)
            if result is None:
                return {"code": 404, "message": "课程不存在或无法更新", "data": None}
            return {"code": 0, "message": "课程状态已更新", "data": result}
        except ValueError as e:
            return {"code": 400, "message": str(e), "data": None}
        except Exception as e:
            return {"code": 500, "message": f"更新课程状态失败: {e}", "data": None}

    def get_learning_path(self, course_id: int, profile_id: Optional[int] = None) -> Dict[str, Any]:
        """获取课程知识点学习路径图谱（含掌握度）。"""
        try:
            path_data = self._repo.get_learning_path(course_id, profile_id=profile_id)
            return {"code": 0, "message": "success", "data": path_data}
        except Exception as e:
            return {"code": 500, "message": f"获取学习路径失败: {e}", "data": None}

    def recommend_resources(self, profile_id: int, course_id: int) -> List[Dict[str, Any]]:
        """
        根据画像推荐资源。

        排序逻辑:
        1. 低 mastery 知识点优先
        2. 匹配学生资源偏好
        3. 未学习过的资源
        4. 教师审核通过资源
        """
        try:
            resources = self._repo.get_recommended_resources(profile_id, course_id)
            return resources
        except Exception as e:
            return []
