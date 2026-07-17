import tempfile
import unittest
from types import SimpleNamespace
from typing import TypedDict
from unittest.mock import Mock, patch

from langgraph.graph import END, START, StateGraph

from app.agents import workflow as workflow_module
from app.agents.workflow import stream_workflow


class _CheckpointState(TypedDict):
    value: int


class WorkflowStreamTests(unittest.TestCase):
    def test_sqlite_checkpointer_survives_connection_restart(self):
        builder = StateGraph(_CheckpointState)
        builder.add_node("increment", lambda state: {"value": state["value"] + 1})
        builder.add_edge(START, "increment")
        builder.add_edge("increment", END)
        config = {"configurable": {"thread_id": "persistent-run"}}

        with tempfile.TemporaryDirectory() as data_dir, patch(
            "app.config.get_settings",
            return_value=SimpleNamespace(app_data_dir=data_dir),
        ):
            try:
                first = workflow_module._get_checkpointer()
                first_graph = builder.compile(checkpointer=first)
                first_graph.invoke({"value": 1}, config)
                self.assertEqual(first_graph.get_state(config).values["value"], 2)

                workflow_module._checkpoint_connection.close()
                workflow_module._checkpointer = None
                workflow_module._checkpoint_connection = None

                second = workflow_module._get_checkpointer()
                second_graph = builder.compile(checkpointer=second)
                self.assertEqual(second_graph.get_state(config).values["value"], 2)
            finally:
                if workflow_module._checkpoint_connection is not None:
                    workflow_module._checkpoint_connection.close()
                workflow_module._checkpointer = None
                workflow_module._checkpoint_connection = None

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
