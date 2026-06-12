"""学生画像 Service"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.repositories.profile_repo import ProfileRepository


class ProfileService:
    """学生画像 Service（委托 Repository 完成数据库操作）"""

    def __init__(self):
        self._repo = ProfileRepository()

    # ------------------------------------------------------------------
    # list_profiles
    # ------------------------------------------------------------------

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
            items, total = self._repo.list_profiles(
                page=page,
                page_size=page_size,
                course_id=course_id,
                keyword=keyword,
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
        except Exception as e:
            return {
                "code": 500,
                "message": f"查询失败: {e}",
                "data": None,
            }

    # ------------------------------------------------------------------
    # get_profile
    # ------------------------------------------------------------------

    def get_profile(self, profile_id: int, user: Any) -> Dict[str, Any]:
        """
        获取单个学生画像详情。

        Args:
            profile_id: 画像 ID
            user: 当前登录用户（FastAPI Depends 注入，当前未使用）

        Returns:
            标准响应 dict：{code, message, data: profile_dict 或 None}
        """
        try:
            profile = self._repo.get_profile(profile_id)
            if profile is None:
                return {"code": 404, "message": "画像不存在", "data": None}
            return {"code": 0, "message": "success", "data": profile}
        except Exception as e:
            return {"code": 500, "message": f"查询失败: {e}", "data": None}

    # ------------------------------------------------------------------
    # update_profile
    # ------------------------------------------------------------------

    def update_profile(
        self, profile_id: int, data: Dict[str, Any], user: Any
    ) -> Dict[str, Any]:
        """
        更新学生画像字段。

        支持更新的字段：
            learning_goal, current_level, interests,
            resource_preferences, weekly_hours, mastery_score

        Args:
            profile_id: 画像 ID
            data: 要更新的字段字典
            user: 当前登录用户（FastAPI Depends 注入，当前未使用）

        Returns:
            标准响应 dict：{code, message, data: 更新后的 profile_dict 或 None}
        """
        try:
            updated = self._repo.update_profile(profile_id, data)
            if updated is None:
                return {"code": 404, "message": "画像不存在", "data": None}
            return {"code": 0, "message": "更新成功", "data": updated}
        except Exception as e:
            return {"code": 500, "message": f"更新失败: {e}", "data": None}

    # ------------------------------------------------------------------
    # update_mastery
    # ------------------------------------------------------------------

    def update_mastery(
        self, profile_id: int, data: Dict[str, Any], user: Any
    ) -> Dict[str, Any]:
        """
        更新或插入知识点掌握度记录。

        请求 data 应包含：
            kp_id: int           - 知识点 ID
            mastery: float       - 掌握度（0~1）
            update_reason: str   - 更新原因（可选）

        Args:
            profile_id: 画像 ID
            data: 包含 kp_id 和 mastery 的字典
            user: 当前登录用户（FastAPI Depends 注入，当前未使用）

        Returns:
            标准响应 dict：{code, message, data: {kp_id, new_mastery} 或 None}
        """
        try:
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
        except Exception as e:
            return {"code": 500, "message": f"掌握度更新失败: {e}", "data": None}
