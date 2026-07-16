import unittest
from unittest.mock import Mock, patch

from app.agents.workflow import stream_workflow


class WorkflowStreamTests(unittest.TestCase):
    @patch("app.agents.workflow.get_compiled_graph")
    def test_done_event_preserves_quality_and_audit_metadata(self, get_graph):
        graph = Mock()
        graph.stream.return_value = iter([
            {
                "teacher_review": {
                    "current_step": "teacher_review",
                    "quality_score": 8.4,
                    "step_history": [
                        {"step": "teacher_review", "status": "success", "duration_ms": 12}
                    ],
                }
            }
        ])
        graph.get_state.return_value = Mock(values={
            "run_id": "run-test",
            "quality_score": 8.4,
            "revision_count": 1,
            "step_history": [
                {"step": "teacher_review", "status": "success", "duration_ms": 12}
            ],
            "generated_resource": {"title": "测试资源"},
            "metadata": {},
        })
        get_graph.return_value = graph

        events = list(stream_workflow(1, 2, [3], "lecture", "basic"))

        done = events[-1]
        metadata = done["result"]["metadata"]
        self.assertEqual(metadata["quality_score"], 8.4)
        self.assertEqual(metadata["revision_count"], 1)
        self.assertEqual(metadata["run_id"], "run-test")
        self.assertEqual(metadata["step_history"][0]["step"], "teacher_review")
        self.assertGreaterEqual(metadata["total_duration_ms"], 0)


if __name__ == "__main__":
    unittest.main()
