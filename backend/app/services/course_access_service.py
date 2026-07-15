"""统一课程级访问控制，防止通过 ID 枚举读取跨课程数据。"""

from typing import Any, Dict, List, Optional

from app.repositories.course_access_repo import CourseAccessRepository
from app.utils.exceptions import ForbiddenException, NotFoundException


class CourseAccessService:
    def __init__(self) -> None:
        self._repo = CourseAccessRepository()

    def require_course_access(self, course_id: int, user: Dict[str, Any]) -> None:
        teacher_id = self._repo.get_course_teacher_id(course_id)
        if teacher_id is None:
            raise NotFoundException("课程不存在")

        user_id = int(user["user_id"])
        roles = set(user.get("roles", []))
        if "admin" in roles:
            return
        if "teacher" in roles and teacher_id == user_id:
            return
        if "student_member" in roles and self._repo.is_student_enrolled(course_id, user_id):
            return
        raise ForbiddenException("无权访问该课程数据")

    def list_accessible_course_ids(self, user: Dict[str, Any]) -> Optional[List[int]]:
        roles = set(user.get("roles", []))
        if "admin" in roles:
            return None
        return self._repo.list_accessible_course_ids(
            user_id=int(user["user_id"]),
            is_teacher="teacher" in roles,
            is_student="student_member" in roles,
        )

    def require_material_access(self, material_id: int, user: Dict[str, Any]) -> int:
        return self._require_entity_course(
            self._repo.get_material_course_id(material_id), user, "资料不存在"
        )

    def require_resource_access(self, resource_id: int, user: Dict[str, Any]) -> int:
        return self._require_entity_course(
            self._repo.get_resource_course_id(resource_id), user, "资源不存在"
        )

    def require_kp_link_access(self, link_id: int, user: Dict[str, Any]) -> int:
        return self._require_entity_course(
            self._repo.get_kp_link_course_id(link_id), user, "知识点关联不存在"
        )

    def require_evidence_link_access(self, link_id: int, user: Dict[str, Any]) -> int:
        return self._require_entity_course(
            self._repo.get_evidence_link_course_id(link_id), user, "证据关联不存在"
        )

    def require_task_access(self, task_id: int, user: Dict[str, Any]) -> int:
        return self._require_entity_course(
            self._repo.get_task_course_id(task_id), user, "任务不存在"
        )

    def require_profile_access(self, profile_id: int, user: Dict[str, Any]) -> int:
        context = self._repo.get_profile_access_context(profile_id)
        if context is None:
            raise NotFoundException("学生画像不存在")

        user_id = int(user["user_id"])
        roles = set(user.get("roles", []))
        course_id = int(context["course_id"])
        if "admin" in roles or int(context["student_id"]) == user_id:
            return course_id
        if "teacher" in roles:
            self.require_course_access(course_id, user)
            return course_id
        raise ForbiddenException("无权访问该学生画像")

    def require_tutor_session_access(
        self, session_id: int, user: Dict[str, Any]
    ) -> int:
        context = self._repo.get_tutor_session_context(session_id)
        if context is None:
            raise NotFoundException("答疑会话不存在")
        if context["course_id"] != context["profile_course_id"]:
            raise ForbiddenException("答疑会话与学生画像课程不一致")
        self.require_profile_access(context["profile_id"], user)
        return context["course_id"]

    def require_profile_course(
        self,
        profile_id: int,
        course_id: int,
        user: Dict[str, Any],
    ) -> None:
        self.require_course_access(course_id, user)
        profile_course_id = self._repo.get_profile_course_id(profile_id)
        if profile_course_id is None:
            raise NotFoundException("学生画像不存在")
        if profile_course_id != course_id:
            raise ForbiddenException("学生画像不属于该课程")

    def _require_entity_course(
        self,
        course_id: Optional[int],
        user: Dict[str, Any],
        missing_message: str,
    ) -> int:
        if course_id is None:
            raise NotFoundException(missing_message)
        self.require_course_access(course_id, user)
        return course_id
