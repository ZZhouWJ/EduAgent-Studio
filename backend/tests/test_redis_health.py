import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import _check_redis_connection, create_app


class RedisHealthTests(unittest.TestCase):
    @patch("app.main.Redis.from_url")
    def test_redis_health_reports_success_and_closes_client(self, from_url):
        client = Mock()
        client.ping.return_value = True
        from_url.return_value = client

        result = _check_redis_connection("redis://localhost:6379/0")

        self.assertEqual(result, {"connected": True})
        client.close.assert_called_once_with()

    @patch("app.main.Redis.from_url")
    def test_redis_health_hides_connection_errors(self, from_url):
        from_url.side_effect = RuntimeError("redis://user:secret@example.invalid")

        result = _check_redis_connection("redis://user:secret@example.invalid")

        self.assertEqual(result, {"connected": False})

    def test_dependency_health_failures_return_http_503(self):
        client = TestClient(create_app())

        with patch(
            "app.main._check_redis_connection", return_value={"connected": False}
        ):
            redis_response = client.get("/api/health/redis")
        with patch(
            "app.main.test_connection",
            return_value={
                "connected": False,
                "message": "数据库连接失败",
                "server_version": None,
            },
        ):
            database_response = client.get("/api/health/db")

        self.assertEqual(redis_response.status_code, 503)
        self.assertEqual(redis_response.json()["code"], 5003)
        self.assertEqual(database_response.status_code, 503)
        self.assertEqual(database_response.json()["code"], 5002)

    def test_liveness_does_not_depend_on_database_or_redis(self):
        client = TestClient(create_app())

        with patch("app.main.test_connection", side_effect=RuntimeError), patch(
            "app.main._check_redis_connection", side_effect=RuntimeError
        ):
            response = client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["status"], "ok")

    def test_root_hides_disabled_production_docs(self):
        settings = Settings(
            APP_ENV="production",
            JWT_SECRET_KEY="a-secure-production-secret-key-with-32-chars",
            API_KEY_SECRET="another-secure-production-key-32-chars",
            CORS_ORIGINS="https://eduagent.example.com",
            LLM_API_KEY="test-key",
            _env_file=None,
        )

        with patch("app.main.get_settings", return_value=settings):
            app = create_app()
            response = TestClient(app).get("/")

        self.assertIsNone(app.docs_url)
        self.assertIsNone(response.json()["data"]["docs"])


if __name__ == "__main__":
    unittest.main()
