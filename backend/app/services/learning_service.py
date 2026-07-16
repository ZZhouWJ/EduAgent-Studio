"""学习服务 — 课程、知识点、学习任务"""

import logging

from typing import Any, Dict, List, Optional

from app.database import get_db_transaction
from app.repositories import LearningRepository, user_repo
from app.services.course_access_service import CourseAccessService
from app.utils.exceptions import ForbiddenException, NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class LearningService:
    """学习服务层，委托给 LearningRepository 执行数据库操作。"""

    def __init__(self) -> None:
        self._repo = LearningRepository()
        self._access = CourseAccessService()

    def list_courses(self, user: Dict[str, Any]) -> Dict[str, Any]:
        course_ids = self._access.list_accessible_course_ids(user)
        return {
            "code": 0,
            "message": "success",
            "data": self._repo.list_courses(course_ids=course_ids),
        }

    def get_course(self, course_id: int) -> Dict[str, Any]:
        course = self._repo.get_course(course_id)
        if course is None:
            return {"code": 404, "message": "课程不存在", "data": None}
        return {"code": 0, "message": "success", "data": course}

    def list_tasks(
        self,
        user: Dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        course_ids = self._access.list_accessible_course_ids(user)
        if course_id is not None:
            self._access.require_course_access(course_id, user)
        roles = set(user.get("roles", []))
        is_student_only = "student_member" in roles and not roles.intersection(
            {"teacher", "admin"}
        )
        assignee_user_id = int(user["user_id"]) if is_student_only else None
        visible_statuses = (
            ["assigned", "in_progress", "completed"] if is_student_only else None
        )
        return {
            "code": 0,
            "message": "success",
            "data": self._repo.list_tasks(
                page=page,
                page_size=page_size,
                course_id=course_id,
                course_ids=course_ids,
                status=status,
                assignee_user_id=assignee_user_id,
                visible_statuses=visible_statuses,
            ),
        }

    def get_task(self, task_id: int) -> Dict[str, Any]:
        task = self._repo.get_task(task_id)
        if task is None:
            return {"code": 404, "message": "任务不存在", "data": None}
        return {"code": 0, "message": "success", "data": task}

    def create_task(
        self,
        course_id: int,
        title: str,
        description: Optional[str] = None,
        target_kp_ids: Optional[list] = None,
        assignee_id: Optional[int] = None,
        due_date: Optional[str] = None,
        creator_id: int = 0,
    ) -> Dict[str, Any]:
        try:
            result = self._repo.create_task(
                course_id=course_id,
                title=title,
                description=description,
                target_kp_ids=target_kp_ids,
                assignee_id=assignee_id,
                due_date=due_date,
                creator_id=creator_id,
            )
            return {"code": 0, "message": "任务创建成功", "data": result}
        except Exception:
            logger.exception("创建学习任务失败: course_id=%s", course_id)
            return {"code": 500, "message": "创建任务失败，请稍后重试", "data": None}

    def update_task_status(
        self,
        user: Dict[str, Any],
        task_id: int,
        status: str,
    ) -> Dict[str, Any]:
        """按角色和状态迁移规则更新学习任务。"""
        self._access.require_task_update_access(task_id, user)
        task = self._repo.get_task(task_id)
        if task is None:
            raise NotFoundException("任务不存在")

        valid_statuses = {"draft", "assigned", "in_progress", "completed", "archived"}
        if status not in valid_statuses:
            raise ValidationException("无效的学习任务状态")

        roles = set(user.get("roles", []))
        current_status = str(task["status"])
        if "student_member" in roles and not roles.intersection({"teacher", "admin"}):
            allowed_transitions = {
                "assigned": {"in_progress", "completed"},
                "in_progress": {"completed"},
                "completed": {"completed"},
            }
            if status not in allowed_transitions.get(current_status, set()):
                raise ForbiddenException("学生不能执行该任务状态变更")

        with get_db_transaction() as conn:
            affected = self._repo.update_task_status(task_id, status, conn=conn)
            if affected == 0 and status != current_status:
                raise NotFoundException("任务不存在或无法更新")
            user_repo.insert_operation_log_with_conn(
                user_id=int(user["user_id"]),
                action_type="learning_task:update_status",
                action_desc=f"学习任务状态: {current_status} -> {status}",
                target_type="learning_task",
                target_id=task_id,
                project_id=None,
                task_id=None,
                conn=conn,
            )
        updated = {**task, "status": status}
        return {"code": 0, "message": "任务状态已更新", "data": updated}

    def update_course_status(self, course_id: int, status: str) -> Dict[str, Any]:
        try:
            result = self._repo.update_course_status(course_id, status)
            if result is None:
                return {"code": 404, "message": "课程不存在或无法更新", "data": None}
            return {"code": 0, "message": "课程状态已更新", "data": result}
        except ValueError as e:
            return {"code": 400, "message": str(e), "data": None}
        except Exception:
            logger.exception("更新课程状态失败: course_id=%s", course_id)
            return {"code": 500, "message": "更新课程状态失败，请稍后重试", "data": None}

    def get_learning_path(self, course_id: int, profile_id: Optional[int] = None) -> Dict[str, Any]:
        """获取课程知识点学习路径图谱（含掌握度）。"""
        try:
            path_data = self._repo.get_learning_path(course_id, profile_id=profile_id)
            return {"code": 0, "message": "success", "data": path_data}
        except Exception:
            logger.exception("获取学习路径失败: course_id=%s", course_id)
            return {"code": 500, "message": "获取学习路径失败，请稍后重试", "data": None}

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
        except Exception:
            logger.exception(
                "获取推荐资源失败: profile_id=%s course_id=%s",
                profile_id,
                course_id,
            )
            return []
