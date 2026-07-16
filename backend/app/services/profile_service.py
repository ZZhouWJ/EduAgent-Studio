"""学生画像 Service"""
import logging
from typing import Any, Dict, Optional

from app.repositories.profile_repo import ProfileRepository
from app.services.course_access_service import CourseAccessService
from app.utils.exceptions import ForbiddenException, NotFoundException

logger = logging.getLogger(__name__)


class ProfileService:
    """学生画像 Service（委托 Repository 完成数据库操作）"""

    def __init__(self):
        self._repo = ProfileRepository()
        self._access = CourseAccessService()

    def require_profile_access(self, profile_id: int, user: Any) -> None:
        """仅画像本人、所属课程教师或管理员可以访问画像私有数据。"""
        self._access.require_profile_access(profile_id, user)

    def list_profiles(
        self,
        user: Any,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        获取学生画像列表（分页）。

        Args:
            user: 当前登录用户（FastAPI Depends 注入，当前未使用）
            page: 页码（从 1 开始）
            page_size: 每页条数
            course_id: 可选，按课程 ID 过滤
            keyword: 可选，按学生姓名或学号关键字搜索

        Returns:
            标准响应 dict：{code, message, data: {items, total, page, page_size}}
        """
        try:
            accessible_course_ids = self._access.list_accessible_course_ids(user)
            if course_id is not None:
                self._access.require_course_access(course_id, user)

            items, total = self._repo.list_profiles(
                page=page,
                page_size=page_size,
                course_id=course_id,
                keyword=keyword,
                course_ids=accessible_course_ids if course_id is None else None,
            )
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "items": items,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
            }
        except (ForbiddenException, NotFoundException):
            raise
        except Exception as e:
            logger.error("查询学生画像列表失败 (%s)", type(e).__name__)
            return {
                "code": 500,
                "message": "查询失败，请稍后重试",
                "data": None,
            }

    def get_profile(self, profile_id: int, user: Any) -> Dict[str, Any]:
        """
        获取单个学生画像详情。
        """
        try:
            self.require_profile_access(profile_id, user)
            profile = self._repo.get_profile(profile_id)
            if profile is None:
                return {"code": 404, "message": "画像不存在", "data": None}
            return {"code": 0, "message": "success", "data": profile}
        except (ForbiddenException, NotFoundException):
            raise
        except Exception as e:
            logger.error("查询学生画像失败: profile_id=%s (%s)", profile_id, type(e).__name__)
            return {"code": 500, "message": "查询失败，请稍后重试", "data": None}

    def get_my_profile(self, user: Any) -> Dict[str, Any]:
        """
        获取当前登录用户自己的学生画像。

        Args:
            user: 当前登录用户，期望包含 user_id 字段

        Returns:
            标准响应 dict：{code, message, data: profile}
        """
        try:
            user_id = user.get("user_id")
            if not user_id:
                return {"code": 401, "message": "无法获取用户身份", "data": None}
            profile = self._repo.get_profile_by_student_id(int(user_id))
            if profile is None:
                return {"code": 404, "message": "您还没有创建学生画像，请先通过学习反馈或教师导入建立画像", "data": None}
            return {"code": 0, "message": "success", "data": profile}
        except Exception as e:
            logger.error("查询本人学生画像失败 (%s)", type(e).__name__)
            return {"code": 500, "message": "查询失败，请稍后重试", "data": None}

    def update_profile(
        self, profile_id: int, data: Dict[str, Any], user: Any
    ) -> Dict[str, Any]:
        """
        更新学生画像字段。
        """
        try:
            self.require_profile_access(profile_id, user)
            updated = self._repo.update_profile(profile_id, data)
            if updated is None:
                return {"code": 404, "message": "画像不存在", "data": None}
            return {"code": 0, "message": "更新成功", "data": updated}
        except (ForbiddenException, NotFoundException):
            raise
        except Exception as e:
            logger.error("更新学生画像失败: profile_id=%s (%s)", profile_id, type(e).__name__)
            return {"code": 500, "message": "更新失败，请稍后重试", "data": None}

    def update_mastery(
        self, profile_id: int, data: Dict[str, Any], user: Any
    ) -> Dict[str, Any]:
        """
        更新或插入知识点掌握度记录。
        """
        try:
            self.require_profile_access(profile_id, user)
            kp_id = data.get("kp_id")
            mastery = data.get("mastery")
            update_reason = data.get("update_reason")

            if kp_id is None or mastery is None:
                return {"code": 400, "message": "缺少 kp_id 或 mastery", "data": None}

            result = self._repo.update_mastery(
                profile_id=profile_id,
                kp_id=kp_id,
                mastery_level=float(mastery),
                update_reason=update_reason,
            )
            if result is None:
                return {"code": 404, "message": "画像或知识点不存在", "data": None}
            return {
                "code": 0,
                "message": "掌握度更新成功",
                "data": {
                    "kp_id": result["kp_id"],
                    "kp_name": result.get("kp_name", ""),
                    "new_mastery": result["mastery_level"],
                    "last_test_score": result.get("last_test_score"),
                    "last_test_date": (
                        result["last_test_date"].strftime("%Y-%m-%d")
                        if result.get("last_test_date")
                        else None
                    ),
                },
            }
        except (ForbiddenException, NotFoundException):
            raise
        except Exception as e:
            logger.error("更新学生掌握度失败: profile_id=%s (%s)", profile_id, type(e).__name__)
            return {"code": 500, "message": "掌握度更新失败，请稍后重试", "data": None}
