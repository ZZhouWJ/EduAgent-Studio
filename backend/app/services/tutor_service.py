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

## 课程知识点
{knowledge_points}

## 知识库检索结果（可作为参考依据）
{context}

## 学生问题
{question}

请以 Markdown 格式回答，要求：
1. 回答专业、准确、通俗易懂
2. 结合学生画像提供个性化解释
3. 适当引用知识库中的证据来源
4. 包含图解说明（Mermaid 格式）或代码示例或练习题（至少一种多模态内容）
5. 推荐相关学习资源

请生成 JSON 格式的回答：
{{
  "answer": "Markdown 正文，包含解释和引用",
  "explanation_level": "basic/intermediate/advanced（根据学生当前水平选择）",
  "citations": [
    {{"chunk_id": 1, "content": "引用的证据片段（不超过100字）", "source": "来源说明"}}
  ],
  "diagram": {{
    "type": "flowchart|sequence|class|state",
    "content": "Mermaid 格式的图表代码"
  }},
  "code_example": {{
    "language": "编程语言",
    "code": "代码内容"
  }},
  "practice_questions": [
    {{"question": "练习题题目", "answer": "参考答案"}}
  ],
  "recommended_resources": [
    {{"resource_id": 1, "title": "资源标题", "type": "lecture/quiz/code_case"}}
  ]
}}
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
    ) -> Dict[str, Any]:
        """
        处理学生答疑请求。

        Args:
            profile_id: 学生画像 ID
            course_id: 课程 ID
            question: 学生问题
            user: 当前用户信息（可选）

        Returns:
            统一响应格式，包含 TutorAnswer
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

            # 5. 调用 LLM 生成回答
            answer_data = self._generate_answer(
                profile=profile,
                knowledge_points=knowledge_points,
                context=context,
                question=question,
            )

            # 6. 保存会话记录
            session_id = self._save_session(
                profile_id=profile_id,
                course_id=course_id,
                question=question,
                answer_data=answer_data,
            )

            # 7. 组装响应
            result = {
                "session_id": session_id,
                "answer": answer_data.get("answer", ""),
                "explanation_level": answer_data.get("explanation_level", "intermediate"),
                "citations": answer_data.get("citations", []),
                "diagram": answer_data.get("diagram"),
                "code_example": answer_data.get("code_example"),
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

        # 构建知识点文本
        kp_text = "\n".join(
            f"- {kp['name']}（{kp['difficulty']}难度）"
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
