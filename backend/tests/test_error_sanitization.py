import asyncio
import json
import unittest
from unittest.mock import Mock, patch

import pymysql

from app.database import test_connection
from app.routers.auth import RegisterRequest, register
from app.services.knowledge_service import KnowledgeService
from app.services.learning_service import LearningService
from app.services.profile_service import ProfileService


SECRET = "mysql://root:secret@internal-host/database"


class ErrorSanitizationTests(unittest.TestCase):
    @patch("app.database.get_connection")
    def test_database_health_does_not_return_driver_error(self, get_connection):
        get_connection.side_effect = pymysql.OperationalError(1045, SECRET)

        result = test_connection()

        self.assertFalse(result["connected"])
        self.assertNotIn(SECRET, result["message"])

    def test_knowledge_service_does_not_return_repository_error(self):
        service = KnowledgeService()
        service._repo = Mock()
        service._repo.search_chunks.side_effect = RuntimeError(SECRET)

        result = service.search(1, "事务")

        self.assertEqual(result["code"], 500)
        self.assertNotIn(SECRET, result["message"])

    def test_learning_service_does_not_return_repository_error(self):
        service = LearningService()
        service._repo = Mock()
        service._repo.create_task.side_effect = RuntimeError(SECRET)

        result = service.create_task(1, "测试")

        self.assertEqual(result["code"], 500)
        self.assertNotIn(SECRET, result["message"])

    def test_profile_service_does_not_return_repository_error(self):
        service = ProfileService()
        service._repo = Mock()
        service._access = Mock()
        service._access.list_accessible_course_ids.return_value = [1]
        service._repo.list_profiles.side_effect = RuntimeError(SECRET)

        result = service.list_profiles({"user_id": 7, "roles": ["teacher"]})

        self.assertEqual(result["code"], 500)
        self.assertNotIn(SECRET, result["message"])

    @patch("app.routers.auth.auth_service.register")
    def test_auth_route_does_not_return_unexpected_error(self, register_user):
        register_user.side_effect = RuntimeError(SECRET)
        body = RegisterRequest(
            username="tester",
            password="Pass@1234",
            confirm_password="Pass@1234",
            real_name="测试用户",
        )
        request = Mock()
        request.headers = {}
        request.client = None

        response = asyncio.run(register(request, body))
        payload = json.loads(response.body)

        self.assertEqual(response.status_code, 500)
        self.assertNotIn(SECRET, payload["message"])


if __name__ == "__main__":
    unittest.main()
