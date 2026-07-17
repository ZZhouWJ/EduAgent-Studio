import json
import unittest
from datetime import datetime
from types import SimpleNamespace

from app.services.tutor_supervisor import (
    TutorSupervisor,
    _inject_embed_syntax,
    _result_to_content_block,
)


class StaticGateway:
    def generate(self, messages, config):
        return SimpleNamespace(content="通用模型回答", tool_calls=[])


class ToolCallingThenFailureGateway:
    def __init__(self):
        self.calls = []

    def generate(self, messages, config):
        self.calls.append([dict(message) for message in messages])
        if len(self.calls) == 1:
            return SimpleNamespace(
                content="",
                status="success",
                error=None,
                tool_calls=[{
                    "id": "call_retrieve_1",
                    "type": "function",
                    "function": {
                        "name": "retrieve_knowledge",
                        "arguments": json.dumps(
                            {
                                "query": "事务原子性与隔离性",
                                "student_profile": {"profile_id": 999},
                            },
                            ensure_ascii=False,
                        ),
                    },
                }],
            )
        return SimpleNamespace(
            content="",
            tool_calls=[],
            status="failed",
            error="模型调用失败",
        )


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

    def test_prompt_only_describes_tools_available_for_current_question(self):
        prompt = self.supervisor._build_system_prompt(
            profile={"weak_points": []},
            knowledge_context="",
            candidate_tool_ids=["retrieve_knowledge", "code_case_agent"],
        )

        self.assertIn("retrieve_knowledge", prompt)
        self.assertIn("code_case_agent", prompt)
        self.assertNotIn("quiz_agent", prompt)
        self.assertNotIn(":::", prompt)
        self.assertIn("不要编造或输出内容块 ID", prompt)

    def test_embed_syntax_replaces_fake_ids_and_removes_unresolved_markers(self):
        answer = (
            "实操案例：:::code_case:block_case_001:::\n\n"
            "即时小测：:::quiz:block_quiz_001:::"
        )
        blocks = [{
            "block_id": "block_code_case_agent_a1b2c3d4",
            "block_type": "code_case",
            "title": "SQL 筛选案例",
            "content": {},
        }]

        result = _inject_embed_syntax(answer, blocks)

        self.assertIn(":::code_case:block_code_case_agent_a1b2c3d4:::", result)
        self.assertNotIn("block_case_001", result)
        self.assertNotIn("block_quiz_001", result)
        self.assertNotIn(":::quiz:", result)

    def test_embed_syntax_removes_fake_ids_when_no_blocks_exist(self):
        result = _inject_embed_syntax(
            "案例：:::code_case:block_case_001:::",
            [],
        )

        self.assertEqual(result, "案例：")

    async def test_tool_call_context_and_model_failure_produce_stream_answer(self):
        gateway = ToolCallingThenFailureGateway()
        supervisor = TutorSupervisor(llm_gateway=gateway)
        supervisor._tool_registry = self.registry
        events = []

        async for raw_event in supervisor.run_stream(
            question=self.question,
            profile={"profile_id": 22, "weak_points": []},
            course_id=3,
        ):
            events.append(json.loads(raw_event.removeprefix("data: ").strip()))

        first_tool_arguments = self.registry.calls[0][1]
        self.assertEqual(first_tool_arguments["course_id"], 3)
        self.assertNotIn("student_profile", first_tool_arguments)
        self.assertEqual(gateway.calls[1][-2]["role"], "assistant")
        self.assertEqual(gateway.calls[1][-1]["role"], "tool")
        self.assertEqual(events[-1]["type"], "supervisor.final")
        self.assertEqual(events[-1]["reason"], "model_failure")
        self.assertIn("[引用:41]", events[-1]["content"])

    async def test_tool_call_context_and_model_failure_produce_blocking_answer(self):
        gateway = ToolCallingThenFailureGateway()
        supervisor = TutorSupervisor(llm_gateway=gateway)
        supervisor._tool_registry = self.registry

        result = await supervisor.run(
            question=self.question,
            profile={"profile_id": 22, "weak_points": []},
            course_id=3,
        )

        self.assertIn("[引用:41]", result.final_answer)
        self.assertTrue(result.final_answer.strip())


if __name__ == "__main__":
    unittest.main()
