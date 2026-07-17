import json
import unittest
from datetime import datetime
from types import SimpleNamespace

from app.services.tutor_supervisor import TutorSupervisor, _result_to_content_block


class StaticGateway:
    def generate(self, messages, config):
        return SimpleNamespace(content="通用模型回答", tool_calls=[])


class FakeRegistry:
    def __init__(self):
        self.calls = []

    def select_for_question(self, question):
        return ["retrieve_knowledge", "quiz_agent", "explanation_skill"]

    def get_openai_schemas(self, tool_ids):
        return []

    async def execute(self, tool_id, arguments):
        self.calls.append((tool_id, arguments))
        if tool_id == "retrieve_knowledge":
            return {
                "chunks": [{
                    "chunk_id": 41,
                    "kp_id": 7,
                    "title": "数据库事务",
                    "content": "事务具有原子性与隔离性。",
                    "source": "第 6 页",
                }],
                "count": 1,
            }
        if tool_id == "quiz_agent":
            return {
                "content": "## 题目 1\n原子性保证事务全部成功或全部失败。",
                "quality_score": 0.8,
                "trustworthiness": "medium",
            }
        raise AssertionError(f"unexpected tool: {tool_id}")


class TutorSupervisorFallbackTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.registry = FakeRegistry()
        self.supervisor = TutorSupervisor(llm_gateway=StaticGateway())
        self.supervisor._tool_registry = self.registry
        self.question = "用银行转账解释原子性和隔离性的区别，然后给我 2 道判断题。"

    async def test_run_executes_grounded_fallback_when_provider_skips_tools(self):
        result = await self.supervisor.run(
            question=self.question,
            profile={"weak_points": []},
            course_id=3,
        )

        self.assertEqual([call.tool_id for call in result.tool_calls], ["retrieve_knowledge", "quiz_agent"])
        self.assertEqual(result.citations[0]["chunk_id"], 41)
        self.assertEqual(result.content_blocks[0]["block_type"], "quiz")
        self.assertIn("[引用:41]", result.final_answer)
        self.assertIn(":::quiz:", result.final_answer)
        self.assertEqual(self.registry.calls[1][1]["knowledge_point_ids"], [7])
        self.assertEqual(self.registry.calls[1][1]["question_count"], 2)
        self.assertEqual(self.registry.calls[1][1]["question_type"], "judgment")

    async def test_stream_emits_tool_events_and_grounded_final(self):
        events = []
        async for raw_event in self.supervisor.run_stream(
            question=self.question,
            profile={"weak_points": [], "updated_at": datetime(2026, 7, 17, 12, 0)},
            course_id=3,
        ):
            events.append(json.loads(raw_event.removeprefix("data: ").strip()))

        event_types = [event["type"] for event in events]
        self.assertEqual(event_types[0], "supervisor.started")
        self.assertIn("supervisor.tool_choice", event_types)
        self.assertEqual(event_types.count("tool.completed"), 2)
        self.assertEqual(events[-1]["type"], "supervisor.final")
        self.assertEqual(events[-1]["route"], "deterministic_fallback")
        self.assertIn("[引用:41]", events[-1]["content"])
        self.assertEqual(events[-1]["content_blocks"][0]["block_type"], "quiz")

    async def test_plain_retrieval_is_not_mislabeled_as_learning_plan(self):
        self.assertIsNone(_result_to_content_block("retrieve_knowledge", {"chunks": []}))


if __name__ == "__main__":
    unittest.main()
