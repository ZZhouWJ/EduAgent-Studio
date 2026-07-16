import asyncio
import unittest
from unittest.mock import Mock, patch

from app.routers.resources import get_resource, list_resources
from app.utils.exceptions import NotFoundException


class ResourceAccessTests(unittest.TestCase):
    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_resource_list_uses_accessible_course_scope(self, access_type, repo):
        access = Mock()
        access.list_accessible_course_ids.return_value = [1, 3]
        access_type.return_value = access
        repo.list_resources.return_value = {"items": [], "total": 0}
        user = {"user_id": 7, "roles": ["teacher"]}

        response = asyncio.run(
            list_resources(page=1, page_size=20, kp_id=None, user=user)
        )

        self.assertEqual(response.status_code, 200)
        repo.list_resources.assert_called_once_with(
            page=1,
            page_size=20,
            course_id=None,
            resource_type=None,
            knowledge_point_id=None,
            status=None,
            course_ids=[1, 3],
        )

    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_student_resource_list_is_limited_to_approved(self, access_type, repo):
        access = Mock()
        access.list_accessible_course_ids.return_value = [1]
        access_type.return_value = access
        repo.list_resources.return_value = {
            "items": [{"resource_id": 9, "review_submitted_at": "2026-07-16T10:00:00"}],
            "total": 1,
        }
        user = {"user_id": 8, "roles": ["student_member"]}

        response = asyncio.run(
            list_resources(page=1, page_size=20, kp_id=None, user=user)
        )

        self.assertEqual(repo.list_resources.call_args.kwargs["status"], "approved")
        self.assertNotIn("review_submitted_at", response.body.decode())

    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_course_knowledge_point_filter_checks_ownership(self, access_type, repo):
        access = Mock()
        access.list_accessible_course_ids.return_value = [1]
        access_type.return_value = access
        repo.list_resources.return_value = {"items": [], "total": 0}
        user = {"user_id": 7, "roles": ["teacher"]}

        asyncio.run(
            list_resources(
                page=1,
                page_size=20,
                course_id=1,
                kp_id=4,
                user=user,
            )
        )

        access.require_knowledge_points_course.assert_called_once_with(1, [4])
        self.assertEqual(repo.list_resources.call_args.kwargs["knowledge_point_id"], 4)

    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_student_cannot_open_unapproved_resource(self, access_type, repo):
        access_type.return_value = Mock()
        repo.get_resource.return_value = {"resource_id": 9, "status": "pending_review"}

        with self.assertRaisesRegex(NotFoundException, "资源不存在"):
            asyncio.run(
                get_resource(9, user={"user_id": 8, "roles": ["student_member"]})
            )

    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_student_detail_hides_internal_review_history(self, access_type, repo):
        access_type.return_value = Mock()
        repo.get_resource.return_value = {
            "resource_id": 9,
            "status": "approved",
            "content": "学生可见正文",
            "reviewer_comment": "内部审核意见",
            "review_history": [{"review_id": 31}],
        }

        response = asyncio.run(
            get_resource(9, user={"user_id": 8, "roles": ["student_member"]})
        )

        body = response.body.decode()
        self.assertIn("学生可见正文", body)
        self.assertNotIn("内部审核意见", body)
        self.assertNotIn("review_history", body)

    @patch("app.routers.resources._repo")
    @patch("app.routers.resources.CourseAccessService")
    def test_resource_detail_authorizes_before_read(self, access_type, repo):
        access = Mock()
        access.require_resource_access.side_effect = RuntimeError("denied")
        access_type.return_value = access

        with self.assertRaisesRegex(RuntimeError, "denied"):
            asyncio.run(
                get_resource(
                    9, user={"user_id": 7, "roles": ["teacher"]}
                )
            )

        repo.get_resource.assert_not_called()


if __name__ == "__main__":
    unittest.main()
