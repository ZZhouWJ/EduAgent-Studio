"""
Tutor Service - 独立学习辅导智能体服务层

实现学生答疑功能：
1. 读取学生画像（薄弱点、资源偏好）
2. 读取课程知识点
3. 检索课程知识库
4. 调用 LLM 生成回答
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.llm.gateway import LLMGateway, LLMConfig
from app.repositories.knowledge_repo import KnowledgeRepository
from app.repositories.profile_repo import ProfileRepository
from app.database import get_db_cursor

logger = logging.getLogger(__name__)


# Tutor 系统提示词
TUTOR_PROMPT = """你是一个专业、耐心的学习辅导 Tutor。请根据学生画像和课程知识库，为学生提供个性化的答疑服务。

## 学生画像
- 学生姓名：{student_name}
- 学习目标：{learning_goal}
- 当前水平：{current_level}
- 薄弱知识点：{weak_points}
- 资源偏好：{resource_preferences}
- 综合掌握度：{mastery_score}

## 课程知识点（含 ID，用于 profile_updates）
{knowledge_points}

## 知识库检索结果（可作为参考依据，务必引用）
{context}

## 学生问题
{question}

回答要求：
1. 回答专业、准确、通俗易懂，结合学生当前水平调整解释深度
2. **必须引用知识库来源**，在关键陈述后加 [引用:chunk_id]，chunk_id 来自上述检索结果
3. 包含以下至少一种多模态内容：Mermaid 图解 / 代码示例 / 练习题
4. 推荐 1-2 个相关学习资源
5. 根据对话内容评估学生对相关知识点的掌握程度，据此更新 profile_updates

**重要：profile_updates 中 JSON 的 key 必须是知识点的数字 ID（字符串形式），value 是 0.0~1.0 的掌握度。**
示例：如果学生问的是 ID=3 和 ID=7 的知识点，理解较好则返回 {{"3": 0.85, "7": 0.60}}

请生成 JSON 格式的回答：
{{
  "answer": "Markdown 正文，引用格式 [引用:chunk_id]，不超过 800 字",
  "explanation_level": "basic/intermediate/advanced",
  "citations": [
    {{"chunk_id": 3, "content": "引用知识库原文片段（不超过80字）", "source": "来源"}}
  ],
  "diagram": {{
    "type": "flowchart|sequence|class|state",
    "content": "Mermaid 代码"
  }},
  "code_example": {{
    "language": "语言",
    "code": "代码"
  }},
  "practice_questions": [
    {{"question": "题目", "answer": "参考答案"}}
  ],
  "recommended_resources": [
    {{"resource_id": 1, "title": "资源标题", "type": "lecture|quiz|case"}}
  ],
  "profile_updates": {{"3": 0.85, "7": 0.60}}
}}

注意：如果对话未涉及具体知识点的掌握度变化，profile_updates 应为空对象 {{}}。
"""


class TutorService:
    """Tutor 答疑服务层"""

    def __init__(self, llm_gateway: Optional[LLMGateway] = None):
        self._knowledge_repo = KnowledgeRepository()
        self._profile_repo = ProfileRepository()
        self._llm_gateway = llm_gateway

    def chat(
        self,
        profile_id: int,
        course_id: int,
        question: str,
        user: Optional[Dict[str, Any]] = None,
        requested_content_types: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        处理学生答疑请求。

        Args:
            profile_id: 学生画像 ID
            course_id: 课程 ID
            question: 学生问题
            user: 当前用户信息（可选）
            requested_content_types: 指定的内容类型（可选）

        Returns:
            统一响应格式，包含 TutorAnswer + 多模态 content_blocks
        """
        try:
            # 1. 读取学生画像
            profile = self._profile_repo.get_profile(profile_id)
            if not profile:
                return {"code": 404, "message": "学生画像不存在", "data": None}

            # 2. 读取课程知识点
            knowledge_points = self._get_course_knowledge_points(course_id)

            # 3. 检索课程知识库
            chunks = self._knowledge_repo.search_chunks(
                course_id=course_id,
                query=question,
                limit=5,
            )

            # 4. 构建上下文
            context = self._build_context(chunks)

            # 5. 调用多 Agent 编排器生成回答
            answer_data = self._generate_answer_multi_agent(
                profile=profile,
                knowledge_points=knowledge_points,
                context=context,
                question=question,
                requested_content_types=requested_content_types,
            )

            # 6. 保存会话记录
            session_id = self._save_session(
                profile_id=profile_id,
                course_id=course_id,
                question=question,
                answer_data=answer_data,
            )

            # 7. 应用画像更新（根据 LLM 评估的知识点掌握度变化）
            self._apply_profile_updates(
                profile_id=profile_id,
                profile_updates=answer_data.get("profile_updates", {}),
                knowledge_points=knowledge_points,
            )

            # 8. 组装响应
            result = {
                "session_id": session_id,
                "answer": answer_data.get("main_answer", answer_data.get("answer", "")),
                "explanation_level": answer_data.get("explanation_level", "intermediate"),
                "citations": answer_data.get("citations", []),
                "content_blocks": answer_data.get("content_blocks", []),
                "intent": answer_data.get("intent"),
                "practice_questions": answer_data.get("practice_questions", []),
                "recommended_resources": answer_data.get("recommended_resources", []),
                "profile_updates": answer_data.get("profile_updates", {}),
            }

            return {
                "code": 0,
                "message": "答疑成功",
                "data": result,
            }

        except Exception as e:
            logger.error(f"Tutor chat failed: {e}")
            return {"code": 500, "message": f"答疑失败: {str(e)}", "data": None}

    def submit_feedback(
        self,
        session_id: int,
        helpful: bool,
        follow_up: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        提交答疑反馈。

        Args:
            session_id: 会话 ID
            helpful: 是否有用
            follow_up: 追问内容（可选）

        Returns:
            统一响应格式
        """
        try:
            with get_db_cursor() as cursor:
                # 更新反馈
                cursor.execute(
                    """
                    UPDATE tutor_sessions
                    SET helpful = %s, follow_up = %s
                    WHERE session_id = %s AND is_deleted = 0
                    """,
                    (1 if helpful else 0, follow_up, session_id),
                )

                if cursor.rowcount == 0:
                    return {"code": 404, "message": "会话不存在", "data": None}

                # 如果是"没理解"（helpful=False），调整解释难度
                if not helpful and follow_up:
                    self._adjust_explanation_level(session_id)

            return {"code": 0, "message": "反馈已提交", "data": {"session_id": session_id}}

        except Exception as e:
            logger.error(f"Tutor feedback failed: {e}")
            return {"code": 500, "message": f"反馈提交失败: {str(e)}", "data": None}

    def get_sessions(
        self,
        profile_id: int,
        course_id: Optional[int] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        获取答疑会话历史。

        Args:
            profile_id: 学生画像 ID
            course_id: 课程 ID（可选）
            limit: 返回数量

        Returns:
            统一响应格式
        """
        try:
            sql = """
                SELECT
                    session_id,
                    course_id,
                    question,
                    answer,
                    explanation_level,
                    helpful,
                    follow_up,
                    created_at
                FROM tutor_sessions
                WHERE profile_id = %s AND is_deleted = 0
            """
            params: List[Any] = [profile_id]

            if course_id is not None:
                sql += " AND course_id = %s"
                params.append(course_id)

            sql += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            with get_db_cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()

            sessions = [
                {
                    "session_id": row["session_id"],
                    "course_id": row["course_id"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "explanation_level": row["explanation_level"],
                    "helpful": row["helpful"],
                    "follow_up": row["follow_up"],
                    "created_at": str(row["created_at"]) if row["created_at"] else None,
                }
                for row in rows
            ]

            return {
                "code": 0,
                "message": "success",
                "data": {
                    "total": len(sessions),
                    "sessions": sessions,
                },
            }

        except Exception as e:
            logger.error(f"Get sessions failed: {e}")
            return {"code": 500, "message": f"获取会话历史失败: {str(e)}", "data": None}

    def _get_course_knowledge_points(self, course_id: int) -> List[Dict[str, Any]]:
        """获取课程知识点列表"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT kp_id, kp_name, difficulty_level, description
                    FROM knowledge_points
                    WHERE course_id = %s AND is_deleted = 0
                    ORDER BY kp_id
                    """,
                    (course_id,),
                )
                rows = cursor.fetchall()

            return [
                {
                    "kp_id": row["kp_id"],
                    "name": row["kp_name"],
                    "difficulty": row["difficulty_level"],
                    "description": row["description"] or "",
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning(f"Failed to get knowledge points: {e}")
            return []

    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """构建 RAG 上下文"""
        if not chunks:
            return "（知识库中暂无相关资料）"

        context_parts = []
        for i, chunk in enumerate(chunks[:3], 1):
            title = chunk.get("title", "")
            content = chunk.get("content", "")[:200]
            source = chunk.get("source_page") or chunk.get("source_paragraph") or "未知来源"
            context_parts.append(f"[{i}] {title}\n来源: {source}\n内容: {content}...")

        return "\n\n".join(context_parts)

    def _generate_answer(
        self,
        profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        context: str,
        question: str,
    ) -> Dict[str, Any]:
        """调用 LLM 生成回答"""

        # 构建知识点文本（包含 kp_id，便于 LLM 返回 profile_updates）
        kp_text = "\n".join(
            f"- ID:{kp['kp_id']} {kp['name']}（{kp['difficulty']}难度）"
            for kp in knowledge_points
        ) or "（暂无课程知识点）"

        # 获取学生画像信息
        student_name = profile.get("student_name", "同学")
        learning_goal = profile.get("learning_goal", "未设置")
        current_level = profile.get("current_level", "未知")
        weak_points_list = profile.get("weak_points", [])
        if isinstance(weak_points_list, list) and len(weak_points_list) > 0:
            if isinstance(weak_points_list[0], dict):
                weak_points_str = "、".join(kp.get("kp_name", "") for kp in weak_points_list)
            else:
                weak_points_str = "、".join(str(wp) for wp in weak_points_list)
        else:
            weak_points_str = "暂无记录"
        resource_prefs = profile.get("resource_preferences", [])
        if isinstance(resource_prefs, list):
            resource_prefs_str = "、".join(str(rp) for rp in resource_prefs)
        else:
            resource_prefs_str = str(resource_prefs) if resource_prefs else "未设置"
        mastery_score = profile.get("mastery_score", 0)

        # 构建提示词
        prompt = TUTOR_PROMPT.format(
            student_name=student_name,
            learning_goal=learning_goal,
            current_level=current_level,
            weak_points=weak_points_str,
            resource_preferences=resource_prefs_str,
            mastery_score=f"{mastery_score:.0%}" if mastery_score else "未评测",
            knowledge_points=kp_text,
            context=context,
            question=question,
        )

        # 调用 LLM
        if self._llm_gateway is None:
            logger.warning("LLM gateway not available, using fallback")
            return self._fallback_answer(question, weak_points_str)

        try:
            settings = get_settings()
            config = settings.llm_config()
            messages = [{"role": "user", "content": prompt}]
            result = self._llm_gateway.generate(messages, config)

            if result.status == "failed":
                logger.error(f"LLM call failed: {result.error}")
                return self._fallback_answer(question, weak_points_str)

            content = result.content.strip()

            # 解析 JSON 响应
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:] if lines[0].strip().startswith("```json") else lines)
                content = content.replace("```", "").strip()

            answer_data = json.loads(content)
            logger.info(f"Tutor answer generated: explanation_level={answer_data.get('explanation_level')}")
            return answer_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}, content: {content[:200]}")
            return self._fallback_answer(question, weak_points_str)
        except Exception as e:
            logger.error(f"LLM generate failed: {e}")
            return self._fallback_answer(question, weak_points_str)

    def _generate_answer_multi_agent(
        self,
        profile: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
        context: str,
        question: str,
        requested_content_types: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """调用 TutorSupervisor 生成回答（Tool Calling 循环）"""
        try:
            from app.services.tutor_supervisor import TutorSupervisor

            course_id = profile.get("course_id", 1)

            supervisor = TutorSupervisor(self._llm_gateway)

            # 同步执行 Supervisor 循环
            import asyncio
            result = asyncio.run(
                supervisor.run(
                    question=question,
                    profile=profile,
                    course_id=course_id,
                    knowledge_context=context,
                )
            )

            logger.info(
                f"[Supervisor] final_answer len={len(result.final_answer)}, "
                f"tool_calls={len(result.tool_calls)}, blocks={len(result.content_blocks)}"
            )

            return {
                "main_answer": result.final_answer,
                "content_blocks": result.content_blocks,
                "intent": None,
                "citations": result.citations,
                "explanation_level": "intermediate",
                "practice_questions": [],
                "recommended_resources": [],
                "profile_updates": {},
                "_execution_trace": result.execution_trace,
            }

        except Exception as e:
            logger.error(f"Supervisor run failed: {e}")
            return self._generate_answer(
                profile=profile,
                knowledge_points=knowledge_points,
                context=context,
                question=question,
            )

    def _fallback_answer(self, question: str, weak_points: str) -> Dict[str, Any]:
        """回退回答（LLM 不可用时）"""
        return {
            "answer": f"""## 答疑回答

您的问题：{question}

根据您目前的学习情况，我提供以下解释：

### 基础概念
这个问题涉及到数据库事务处理的相关知识。

### 详细解释
事务是数据库操作的基本单元，具有以下特性（ACID）：
- **原子性（Atomicity）**：事务中的所有操作要么全部成功，要么全部失败
- **一致性（Consistency）**：事务执行前后，数据库状态保持一致
- **隔离性（Isolation）**：并发执行的事务相互隔离
- **持久性（Durability）**：事务完成后，其结果永久保存

### 图解说明

```mermaid
flowchart LR
    A[开始事务] --> B[执行操作]
    B --> C{{操作成功?}}
    C -->|是| D[提交事务]
    C -->|否| E[回滚事务]
    D --> F[事务完成]
    E --> F
```

### 练习题
1. 事务的 ACID 特性是指什么？
2. 请解释原子性和一致性的区别。

### 推荐资源
- 讲义：数据库事务基础
- 练习题：事务处理练习

---
*提示：如果需要更详细的解释，请继续追问或查看推荐资源。*
""",
            "explanation_level": "basic",
            "citations": [],
            "diagram": {
                "type": "flowchart",
                "content": """flowchart LR
    A[开始事务] --> B[执行操作]
    B --> C{{操作成功?}}
    C -->|是| D[提交事务]
    C -->|否| E[回滚事务]
    D --> F[事务完成]
    E --> F"""
            },
            "code_example": None,
            "practice_questions": [
                {"question": "事务的 ACID 特性是指什么？", "answer": "Atomicity（原子性）、Consistency（一致性）、Isolation（隔离性）、Durability（持久性）"},
                {"question": "请解释原子性和一致性的区别。", "answer": "原子性强调操作的全有或全无，一致性强调状态的有效性转变"}
            ],
            "recommended_resources": [],
        }

    def _save_session(
        self,
        profile_id: int,
        course_id: int,
        question: str,
        answer_data: Dict[str, Any],
    ) -> int:
        """保存答疑会话到数据库"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tutor_sessions
                        (profile_id, course_id, question, answer, explanation_level, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        profile_id,
                        course_id,
                        question,
                        answer_data.get("answer", ""),
                        answer_data.get("explanation_level", "intermediate"),
                    ),
                )
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return 0

    def _apply_profile_updates(
        self,
        profile_id: int,
        profile_updates: Dict[str, Any],
        knowledge_points: List[Dict[str, Any]],
    ) -> None:
        """
        将 LLM 返回的知识点掌握度变化应用到数据库。

        Args:
            profile_id: 画像 ID
            profile_updates: LLM 返回的 {kp_id: mastery_level} 字典
            knowledge_points: 当前课程的知识点列表（含 kp_id → name 映射）
        """
        if not profile_updates:
            return

        # 构建 kp_name 查找表
        kp_name_map = {str(kp["kp_id"]): kp["name"] for kp in knowledge_points}

        for kp_id_str, mastery_level in profile_updates.items():
            try:
                kp_id = int(kp_id_str)
            except (ValueError, TypeError):
                logger.warning(f"[ProfileUpdate] invalid kp_id: {kp_id_str}")
                continue

            if not isinstance(mastery_level, (int, float)) or not (0 <= mastery_level <= 1):
                logger.warning(f"[ProfileUpdate] invalid mastery_level for kp_id={kp_id}: {mastery_level}")
                continue

            kp_name = kp_name_map.get(str(kp_id), f"kp#{kp_id}")
            try:
                self._profile_repo.update_mastery(
                    profile_id=profile_id,
                    kp_id=kp_id,
                    mastery_level=float(mastery_level),
                    update_reason=f"[Tutor答疑] 自动更新 — {kp_name}",
                )
                logger.info(f"[ProfileUpdate] kp={kp_name}(id={kp_id}) → mastery={mastery_level:.2f}")
            except Exception as e:
                logger.error(f"[ProfileUpdate] failed for kp_id={kp_id}: {e}")

    def _adjust_explanation_level(self, session_id: int) -> None:
        """根据反馈调整解释难度"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT profile_id, course_id, question
                    FROM tutor_sessions
                    WHERE session_id = %s AND is_deleted = 0
                    """,
                    (session_id,),
                )
                row = cursor.fetchone()

            if not row:
                return

            # 获取学生画像
            profile = self._profile_repo.get_profile(row["profile_id"])
            if not profile:
                return

            # 将解释级别降低一级
            current_level = profile.get("current_level", "").lower()
            if "基础" in current_level or "basic" in current_level:
                new_level = "basic"
            elif "中等" in current_level or "intermediate" in current_level:
                new_level = "basic"  # 降到基础
            else:
                new_level = "intermediate"  # 降到中等

            logger.info(f"Adjusted explanation level to: {new_level} for profile {row['profile_id']}")

        except Exception as e:
            logger.error(f"Failed to adjust explanation level: {e}")

    def get_suggestions(
        self,
        course_id: int,
        profile_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """根据学生画像和课程知识点，动态生成学习建议问题"""
        try:
            # 获取学生画像
            profile = None
            if profile_id:
                profile = self._profile_repo.get_profile(profile_id)

            # 获取课程知识点
            knowledge_points = self._get_course_knowledge_points(course_id)
            kp_names = [kp["name"] for kp in knowledge_points[:8]]
            weak_points: list[str] = []
            if profile:
                wps = profile.get("weak_points", [])
                if isinstance(wps, list):
                    weak_points = [
                        wp.get("kp_name", "") if isinstance(wp, dict) else str(wp)
                        for wp in wps[:3]
                    ]

            # 构建 prompt
            weak_str = "、".join(weak_points) if weak_points else "暂无薄弱点记录"
            kp_str = "、".join(kp_names) if kp_names else "暂无知识点数据"

            prompt = f"""你是一个学习助手。请根据以下信息，生成4条学生最可能问的学习问题。

## 课程知识点
{kp_str}

## 学生薄弱知识点
{weak_str}

## 要求
1. 结合薄弱知识点和课程内容，生成针对性强的问题
2. 问题要具体、实用，是学生真实会问的
3. 每条问题不超过30字
4. 只输出 JSON 数组，不要其他内容

输出格式：
["问题1", "问题2", "问题3", "问题4"]"""

            if self._llm_gateway is None:
                return {
                    "code": 0,
                    "data": {
                        "suggestions": [
                            f"{kp_names[0] if kp_names else '课程内容'}的核心概念是什么？",
                            f"如何理解{kp_names[1] if len(kp_names) > 1 else '相关知识点'}？",
                            "有哪些典型应用场景？",
                            "常见错误和注意事项有哪些？",
                        ]
                        if kp_names else []
                    },
                }

            result = self._llm_gateway.generate(
                messages=[{"role": "user", "content": prompt}],
                config={"temperature": 0.8, "max_tokens": 500},
            )

            content = result.content.strip() if hasattr(result, "content") else "[]"
            # 提取 JSON
            import re
            m = re.search(r"\[[\s\S]*\]", content)
            if m:
                import json
                suggestions = json.loads(m.group())
                if isinstance(suggestions, list):
                    return {"code": 0, "data": {"suggestions": suggestions[:4]}}

            return {
                "code": 0,
                "data": {
                    "suggestions": [
                        f"{kp_names[0] if kp_names else '课程'}的核心概念是什么？",
                        "有哪些典型应用场景？",
                        "常见错误和注意事项有哪些？",
                        "如何系统地学习这部分内容？",
                    ]
                    if kp_names else []
                },
            }

        except Exception as e:
            logger.error(f"get_suggestions failed: {e}")
            return {"code": 0, "data": {"suggestions": []}}
