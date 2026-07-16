import asyncio
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from app.services.agent_service import (
    AgentService,
    _extract_save_payload,
    extract_resource_references,
)
from app.routers.agents import GenerateRequest, generate_learning_resource


class ExtractSavePayloadTests(unittest.TestCase):
    def test_accepts_streamed_workflow_result(self):
        result = {
            "resource": {
                "title": "事务隔离级别讲义",
                "type": "lecture",
                "content": "不可重复读与幻读的区别",
                "difficulty": "intermediate",
                "knowledge_points": [7],
            },
            "evidence_links": [{"chunk_id": 12, "quote_text": "隔离级别定义"}],
            "trustworthiness": "high",
            "metadata": {
                "quality_score": 8.6,
                "step_history": [{"step": "generation", "status": "success"}],
            },
        }

        payload = _extract_save_payload(result)

        self.assertEqual(payload["resource"]["content"], "不可重复读与幻读的区别")
        self.assertEqual(payload["evidence_links"][0]["chunk_id"], 12)
        self.assertEqual(payload["trustworthiness"], "high")
        self.assertEqual(payload["quality_score"], 8.6)

    def test_prefers_synchronous_raw_result(self):
        result = {
            "resource": {"content": "mapped"},
            "_raw": {
                "generated_resource": {"content": "raw"},
                "trustworthiness": "medium",
            },
        }

        payload = _extract_save_payload(result)

        self.assertEqual(payload["resource"]["content"], "raw")
        self.assertEqual(payload["trustworthiness"], "medium")

    def test_extracts_and_deduplicates_resource_references(self):
        result = {
            "resource": {"target_kp_ids": "4,5,4"},
            "evidence_links": [
                {"chunk_id": 8},
                {"chunk_id": 9},
                {"chunk_id": 8},
            ],
        }

        references = extract_resource_references(result)

        self.assertEqual(references, {"kp_ids": [4, 5], "chunk_ids": [8, 9]})


class AgentContextTests(unittest.TestCase):
    def test_generation_request_rejects_unsupported_resource_type(self):
        with self.assertRaises(ValidationError):
            GenerateRequest(
                student_id=12,
                course_id=3,
                knowledge_point_ids=[4],
                resource_type="unsupported",
                difficulty="intermediate",
            )

    @patch("app.repositories.profile_repo.ProfileRepository")
    def test_profile_resolution_uses_student_and_course(self, repo_type):
        repo = Mock()
        repo.get_profile_by_student_and_course.return_value = {
            "profile_id": 22,
            "course_id": 3,
        }
        repo_type.return_value = repo

        profile_id, profile = AgentService()._resolve_profile(12, 3)

        self.assertEqual(profile_id, 22)
        self.assertEqual(profile["course_id"], 3)
        repo.get_profile_by_student_and_course.assert_called_once_with(12, 3)

    @patch("app.repositories.learning_feedback_repo.LearningFeedbackRepository")
    def test_learning_history_is_scoped_to_student_and_course(self, repo_type):
        repo = Mock()
        repo.list_feedbacks.return_value = {"items": []}
        repo_type.return_value = repo

        AgentService()._load_learning_history(12, 3)

        repo.list_feedbacks.assert_called_once_with(
            page=1, page_size=10, course_id=3, student_id=12
        )

    @patch("app.routers.agents.AgentService")
    @patch("app.routers.agents.CourseAccessService")
    def test_generate_route_authorizes_before_service(self, access_type, service_type):
        access = Mock()
        access_type.return_value = access
        service = Mock()
        service.generate.return_value = {"code": 0, "message": "success", "data": {}}
        service_type.return_value = service
        request = GenerateRequest(
            student_id=12,
            course_id=3,
            knowledge_point_ids=[4],
            resource_type="lecture",
            difficulty="intermediate",
        )
        user = {"user_id": 7, "roles": ["teacher"]}

        result = asyncio.run(generate_learning_resource(request, user))

        self.assertEqual(result["code"], 0)
        access.require_generation_context.assert_called_once_with(3, 12, [4], user)


if __name__ == "__main__":
    unittest.main()
