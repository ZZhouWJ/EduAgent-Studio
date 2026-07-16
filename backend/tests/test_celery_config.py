import unittest

from app.celery_app import celery_app


class CeleryConfigTests(unittest.TestCase):
    def test_only_real_embedding_tasks_are_registered(self):
        self.assertEqual(celery_app.conf.include, ["app.tasks.embedding_tasks"])
        self.assertFalse(celery_app.conf.beat_schedule)


if __name__ == "__main__":
    unittest.main()
