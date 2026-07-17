import json
import unittest
from unittest.mock import Mock, patch

from app.routers.tutor import ChatRequest, tutor_chat_stream


class FakeSupervisor:
    async def run_stream(self, **kwargs):
        yield 'data: {"type":"supervisor.started"}\n\n'
        yield 'data: {"type":"supervisor.final","content":"grounded answer","content_blocks":[],"citations":[]}\n\n'


class TutorStreamPersistenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_final_event_contains_persisted_session_id(self):
        service = Mock()
        service.save_stream_session.return_value = 88
        profile_repo = Mock()
        profile_repo.get_profile.return_value = {"student_name": "测试学生"}
        knowledge_repo = Mock()
        knowledge_repo.search_chunks.return_value = []

        with (
            patch("app.routers.tutor.CourseAccessService") as access_type,
            patch("app.routers.tutor._get_tutor_service", return_value=service),
            patch("app.routers.tutor.ProfileRepository", return_value=profile_repo),
            patch("app.routers.tutor.KnowledgeRepository", return_value=knowledge_repo),
            patch("app.routers.tutor.TutorSupervisor", return_value=FakeSupervisor()),
        ):
            response = await tutor_chat_stream(
                ChatRequest(profile_id=22, course_id=3, question="question"),
                user={"user_id": 12, "roles": ["student_member"]},
            )
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk.decode() if isinstance(chunk, bytes) else chunk)

        access_type.return_value.require_profile_course.assert_called_once()
        service.save_stream_session.assert_called_once()
        final_line = next(line for line in "".join(chunks).splitlines() if "supervisor.final" in line)
        event = json.loads(final_line.removeprefix("data: "))
        self.assertEqual(event["session_id"], 88)
        self.assertEqual(event["content"], "grounded answer")


if __name__ == "__main__":
    unittest.main()
