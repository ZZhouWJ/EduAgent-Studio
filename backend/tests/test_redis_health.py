import unittest
from unittest.mock import Mock, patch

from app.main import _check_redis_connection


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


if __name__ == "__main__":
    unittest.main()
