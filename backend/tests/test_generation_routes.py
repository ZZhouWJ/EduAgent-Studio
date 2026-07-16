import unittest

from app.main import create_app


class GenerationRouteTests(unittest.TestCase):
    def test_only_multi_agent_generation_route_is_exposed(self):
        app = create_app()
        paths = app.openapi()["paths"]

        self.assertIn("post", paths["/api/agents/generate"])
        self.assertIn("post", paths["/api/agents/generate/stream"])
        self.assertNotIn("/api/tasks/{task_id}/generate", paths)


if __name__ == "__main__":
    unittest.main()
