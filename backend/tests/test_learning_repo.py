from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch

from app.repositories.learning_repo import LearningRepository, _current_semester


class LearningRepositoryTests(unittest.TestCase):
    def test_detects_task_types_from_titles(self):
        repository = LearningRepository()

        self.assertEqual(repository._detect_task_type("SQL 多表连接练习"), "exercise")
        self.assertEqual(repository._detect_task_type("事务隔离阶段测验"), "quiz")
        self.assertEqual(repository._detect_task_type("数据库课程项目"), "project")
        self.assertEqual(repository._detect_task_type("索引优化讲义"), "lecture")
        self.assertEqual(repository._detect_task_type("期末复习计划"), "review")

    def test_semester_tracks_academic_calendar(self):
        self.assertEqual(
            _current_semester(datetime(2026, 3, 1)),
            "2025-2026学年春季学期",
        )
        self.assertEqual(
            _current_semester(datetime(2026, 10, 1)),
            "2026-2027学年秋季学期",
        )

    @patch("app.repositories.learning_repo.get_db_cursor")
    def test_recommendations_use_approved_status_and_exact_kp_membership(self, get_cursor):
        cursor = MagicMock()
        cursor.fetchone.side_effect = [{"resource_preferences": None}]
        cursor.fetchall.side_effect = [
            [
                {
                    "kp_id": 1,
                    "kp_name": "事务隔离",
                    "estimated_hours": 1.5,
                    "mastery_level": 0.2,
                }
            ],
            [],
            [
                {
                    "resource_id": 7,
                    "resource_title": "事务隔离练习",
                    "resource_type": "quiz",
                    "difficulty": "intermediate",
                    "target_kp_ids": "1,10",
                    "status": "approved",
                }
            ],
        ]
        context = MagicMock()
        context.__enter__.return_value = cursor
        context.__exit__.return_value = False
        get_cursor.return_value = context

        items = LearningRepository().get_recommended_resources(2, 3)

        resource_sql = cursor.execute.call_args_list[-1].args[0]
        self.assertIn("lr.status = 'approved'", resource_sql)
        self.assertIn("FIND_IN_SET", resource_sql)
        self.assertNotIn("review_status", resource_sql)
        self.assertEqual(items[0]["kp_name"], "事务隔离")
        self.assertEqual(items[0]["estimated_minutes"], 90)


if __name__ == "__main__":
    unittest.main()
