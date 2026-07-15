from datetime import datetime
import unittest

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


if __name__ == "__main__":
    unittest.main()
