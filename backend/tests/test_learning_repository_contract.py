import inspect
import unittest

from app.repositories.learning_repo import LearningRepository


class LearningRepositoryContractTests(unittest.TestCase):
    def test_create_task_is_bound_instance_method(self):
        parameters = inspect.signature(LearningRepository().create_task).parameters
        self.assertNotIn("self", parameters)
        self.assertIn("course_id", parameters)


if __name__ == "__main__":
    unittest.main()
