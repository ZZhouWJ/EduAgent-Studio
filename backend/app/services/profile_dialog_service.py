"""
学生画像对话 Service

处理对话式画像构建的业务逻辑：
1. 保存学生消息
2. 调用 LLM 抽取结构化画像数据
3. 保存助手回复
4. 返回抽取结果供确认和应用
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.llm.runtime import get_runtime_llm_gateway
from app.repositories.profile_dialog_repo import ProfileDialogRepository
from app.repositories.profile_repo import ProfileRepository

logger = logging.getLogger(__name__)


# 画像抽取 Prompt 模板
EXTRACTION_PROMPT = """你是一个学生学习画像分析助手。请从学生的描述中抽取结构化的画像信息。

学生描述：
{user_message}

请抽取以下字段（只返回有信息支持的字段，无信息的字段填 null 或空列表）：

{{
    "knowledge_base": "学生已有知识基础的描述（null表示未知）",
    "current_level": "当前学习水平：基础/一般/较好",
    "cognitive_style": "偏好的理解方式，例如视觉型、例题驱动或结构化阅读",
    "learning_goal": "学生的学习目标（null表示未知）",
    "weak_points": ["薄弱知识点名称1", "薄弱知识点名称2"],
    "error_prone_points": ["易错点1", "易错点2"],
    "interests": ["兴趣方向1", "兴趣方向2"],
    "resource_preferences": ["资源偏好类型1", "资源偏好类型2"],
    "weekly_hours": 每周可学习小时数（数字，null表示未知）,
    "time_constraints": "可学习时段或其他时间限制",
    "practice_level": "实践能力水平描述",
    "motivation": "学习动机"
}}

注意：
1. 只填写真实从学生描述中能推断出的信息，不要编造
2. weak_points、error_prone_points、interests、resource_preferences 为数组（可为空列表 []）
3. weekly_hours 为数字，如"每周3小时"则填 3
4. 只返回 JSON，不要有其他文字
"""


class ProfileDialogService:
    """学生画像对话服务层。"""

    def __init__(self) -> None:
        self._repo = ProfileDialogRepository()
        self._profile_repo = ProfileRepository()
        self._settings = get_settings()

    def chat(
        self, profile_id: int, message: str, user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理对话消息。

        流程：
        1. 保存学生消息到 profile_dialog_messages
        2. 调用 LLM 抽取结构化画像数据
        3. 保存助手回复（包含抽取结果）
        4. 返回：{ reply, extracted, profile_patch, pending_changes }

        Args:
            profile_id: 画像 ID
            message: 学生消息
            user: 当前用户（可选）

        Returns:
            标准响应格式：{code, message, data: {...}}
        """
        try:
            # 1. 保存学生消息
            student_msg_id = self._repo.create_message(
                profile_id=profile_id,
                role="student",
                content=message,
            )

            # 2. 调用 LLM 抽取结构化数据
            extracted_data = self._extract_profile_data(message)

            # 3. 生成助手回复
            reply_text = self._generate_reply(message, extracted_data)

            # 4. 保存助手回复
            assistant_msg_id = self._repo.create_message(
                profile_id=profile_id,
                role="assistant",
                content=reply_text,
                extracted_json=extracted_data,
            )

            # 5. 获取未应用的抽取结果
            pending = self._repo.get_pending_extractions(profile_id)
            pending_changes = [
                {
                    "message_id": p["message_id"],
                    "extracted": p["extracted_json"],
                    "created_at": p["created_at"],
                }
                for p in pending
            ]

            # 6. 构建响应数据
            data = {
                "reply": reply_text,
                "extracted": extracted_data,
                "profile_patch": self._build_profile_patch(extracted_data),
                "pending_changes": pending_changes,
                "student_message_id": student_msg_id,
                "assistant_message_id": assistant_msg_id,
            }

            return {
                "code": 0,
                "message": "success",
                "data": data,
            }

        except Exception as e:
            logger.error("学生画像对话处理失败 (%s)", type(e).__name__)
            return {
                "code": 500,
                "message": "对话处理失败，请稍后重试",
                "data": None,
            }

    def get_dialog_history(
        self, profile_id: int, limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取对话历史。

        Args:
            profile_id: 画像 ID
            limit: 返回条数限制

        Returns:
            标准响应格式
        """
        try:
            messages = self._repo.get_dialog_history(profile_id, limit)
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "profile_id": profile_id,
                    "messages": messages,
                    "total": len(messages),
                },
            }
        except Exception as e:
            logger.error("获取学生画像对话历史失败 (%s)", type(e).__name__)
            return {
                "code": 500,
                "message": "获取对话历史失败，请稍后重试",
                "data": None,
            }

    def get_pending_extractions(
        self, profile_id: int
    ) -> Dict[str, Any]:
        """
        获取未应用的抽取结果。

        Args:
            profile_id: 画像 ID

        Returns:
            标准响应格式
        """
        try:
            pending = self._repo.get_pending_extractions(profile_id)
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "profile_id": profile_id,
                    "pending_changes": [
                        {
                            "message_id": p["message_id"],
                            "extracted": p["extracted_json"],
                            "created_at": p["created_at"],
                        }
                        for p in pending
                    ],
                    "total": len(pending),
                },
            }
        except Exception as e:
            logger.error("获取待应用画像抽取结果失败 (%s)", type(e).__name__)
            return {
                "code": 500,
                "message": "获取待应用抽取结果失败，请稍后重试",
                "data": None,
            }

    def apply_extraction(
        self, profile_id: int, message_id: int
    ) -> Dict[str, Any]:
        """
        应用抽取结果到画像。

        Args:
            profile_id: 画像 ID
            message_id: 消息 ID（包含抽取结果）

        Returns:
            标准响应格式
        """
        try:
            # 获取消息
            pending = self._repo.get_pending_extractions(profile_id)
            target_msg = None
            for p in pending:
                if p["message_id"] == message_id:
                    target_msg = p
                    break

            if not target_msg:
                return {
                    "code": 404,
                    "message": "消息不存在或已应用",
                    "data": None,
                }

            extracted = target_msg["extracted_json"]
            if not extracted:
                return {
                    "code": 400,
                    "message": "消息中没有抽取数据",
                    "data": None,
                }

            # 构建更新数据
            profile_patch = self._build_profile_patch(extracted)
            change_summary = self._generate_change_summary(extracted)
            applied = self._repo.apply_profile_patch(
                profile_id=profile_id,
                message_id=message_id,
                profile_patch=profile_patch,
                change_summary=change_summary,
            )
            if not applied:
                return {
                    "code": 404,
                    "message": "消息不存在、已应用或画像不存在",
                    "data": None,
                }

            updated_profile = self._profile_repo.get_profile(profile_id)

            return {
                "code": 0,
                "message": "应用成功",
                "data": {
                    "profile_id": profile_id,
                    "message_id": message_id,
                    "updated_profile": updated_profile,
                    "change_summary": change_summary,
                },
            }

        except Exception as e:
            logger.error("应用画像抽取结果失败 (%s)", type(e).__name__)
            return {
                "code": 500,
                "message": "应用抽取结果失败，请稍后重试",
                "data": None,
            }

    def _extract_profile_data(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        调用 LLM 抽取结构化画像数据。

        Args:
            user_message: 学生消息

        Returns:
            抽取的结构化数据，或 None
        """
        try:
            config = self._settings.llm_config()

            messages = [
                {"role": "user", "content": EXTRACTION_PROMPT.format(user_message=user_message)}
            ]

            result = get_runtime_llm_gateway().generate(messages, config)

            if result.status == "success" and result.content:
                # 尝试解析 JSON
                json_str = self._extract_json_from_response(result.content)
                if json_str:
                    return json.loads(json_str)

            # 如果 LLM 调用失败或解析失败，返回默认结构
            logger.warning("LLM extraction failed, using default")
            return self._get_default_extraction()

        except Exception as e:
            logger.error("LLM extraction failed (%s)", type(e).__name__)
            return self._get_default_extraction()

    def _extract_json_from_response(self, content: str) -> Optional[str]:
        """
        从 LLM 响应中提取 JSON 字符串。

        尝试多种方式提取：
        1. 直接解析（如果内容是纯 JSON）
        2. 查找 ```json ... ``` 块
        3. 查找 { ... } 块
        """
        content = content.strip()

        # 方式1：直接解析
        try:
            json.loads(content)
            return content
        except Exception:
            pass

        # 方式2：查找 ```json 块
        import re
        json_blocks = re.findall(r'```json\s*([\s\S]*?)\s*```', content)
        for block in json_blocks:
            block = block.strip()
            try:
                json.loads(block)
                return block
            except Exception:
                continue

        # 方式3：查找第一个 { ... }
        json_matches = re.findall(r'\{[\s\S]*\}', content)
        for match in json_matches:
            try:
                json.loads(match)
                return match
            except Exception:
                continue

        return None

    def _generate_reply(
        self, user_message: str, extracted_data: Optional[Dict[str, Any]]
    ) -> str:
        """
        生成助手回复。

        Args:
            user_message: 学生原始消息
            extracted_data: 抽取的结构化数据

        Returns:
            助手回复文本
        """
        if not extracted_data:
            return "谢谢你的分享！我理解了你的学习情况。有什么具体想了解的吗？"

        # 构建一个友好的回复
        parts = ["根据你的描述，我提取了以下学习画像信息："]

        if extracted_data.get("knowledge_base"):
            parts.append(f"\n**知识基础**: {extracted_data['knowledge_base']}")

        if extracted_data.get("current_level"):
            parts.append(f"\n**当前水平**: {extracted_data['current_level']}")

        weak_points = extracted_data.get("weak_points", [])
        if weak_points and any(weak_points):
            parts.append(f"\n**薄弱知识点**: {', '.join(str(p) for p in weak_points if p)}")

        error_prone = extracted_data.get("error_prone_points", [])
        if error_prone and any(error_prone):
            parts.append(f"\n**易错点**: {', '.join(str(p) for p in error_prone if p)}")

        if extracted_data.get("learning_goal"):
            parts.append(f"\n**学习目标**: {extracted_data['learning_goal']}")

        if extracted_data.get("cognitive_style"):
            parts.append(f"\n**认知风格**: {extracted_data['cognitive_style']}")

        parts.append("\n\n请确认这些信息是否准确，或者告诉我需要修改的地方。")

        return "".join(parts)

    def _build_profile_patch(
        self, extracted_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        从抽取数据构建画像更新补丁。

        只映射 service 层支持的字段。
        """
        if not extracted_data:
            return {}

        patch: Dict[str, Any] = {}

        for field in (
            "learning_goal",
            "knowledge_base",
            "current_level",
            "cognitive_style",
            "time_constraints",
            "practice_level",
            "motivation",
        ):
            value = extracted_data.get(field)
            if value:
                patch[field] = str(value).strip()

        for field in ("interests", "resource_preferences"):
            values = extracted_data.get(field)
            if isinstance(values, list) and any(values):
                patch[field] = ",".join(str(value).strip() for value in values if value)

        weekly_hours = extracted_data.get("weekly_hours")
        if isinstance(weekly_hours, (int, float)):
            patch["weekly_hours"] = max(0, min(168, int(weekly_hours)))

        error_prone_points = extracted_data.get("error_prone_points")
        if isinstance(error_prone_points, list) and any(error_prone_points):
            patch["error_prone_points"] = json.dumps(
                [str(point).strip() for point in error_prone_points if point],
                ensure_ascii=False,
            )

        return patch

    def _generate_change_summary(
        self, extracted_data: Dict[str, Any]
    ) -> str:
        """
        生成变更摘要。
        """
        parts = []

        if extracted_data.get("learning_goal"):
            parts.append(f"更新学习目标: {extracted_data['learning_goal']}")

        if extracted_data.get("current_level"):
            parts.append(f"更新当前水平: {extracted_data['current_level']}")

        if extracted_data.get("cognitive_style"):
            parts.append(f"更新认知风格: {extracted_data['cognitive_style']}")

        if extracted_data.get("weekly_hours") is not None:
            parts.append(f"更新每周学习时长: {extracted_data['weekly_hours']} 小时")

        if extracted_data.get("weak_points"):
            weak = extracted_data.get("weak_points", [])
            if isinstance(weak, list) and any(weak):
                parts.append(f"识别薄弱知识点: {', '.join(str(p) for p in weak[:3])}")

        if not parts:
            return "通过对话更新了学习画像"

        return "; ".join(parts)

    def _get_default_extraction(self) -> Dict[str, Any]:
        """
        获取默认抽取结果（LLM 失败时使用）。
        """
        return {
            "knowledge_base": None,
            "current_level": None,
            "weak_points": [],
            "error_prone_points": [],
            "learning_goal": None,
            "cognitive_style": None,
            "interests": [],
            "resource_preferences": [],
            "weekly_hours": None,
            "time_constraints": None,
            "practice_level": None,
            "motivation": None,
        }
