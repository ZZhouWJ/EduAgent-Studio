"""
资源生成智能体

根据学习路径和资源类型生成具体的个性化学习资源。
"""
import logging
import uuid
from typing import Any, Dict, List

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_RESOURCE_GENERATION = """你是一个专业的教育资源生成智能体。请根据以下信息，为学生生成个性化学习资源。

## 学习路径
{learning_path}

## 资源类型：{resource_type}
## 难度：{difficulty}
## 学生信息：{student_info}

请生成一份完整的、高质量的学习资源。

{type_specific_instruction}

## 输出要求
直接输出学习资源内容，使用 Markdown 格式。
内容要求：
- 知识讲解清晰准确，有具体示例
- 练习题有答案和简要解析
- 代码示例可直接运行
- 适合难度：{difficulty}
"""


INSTRUCTION_MAP = {
    "lecture": """## 资源类型要求（讲义）
生成一份知识点讲义，包含：
- 概述：简述本知识点的重要性
- 核心概念：定义和原理
- 详细讲解：分层次展开
- 代码示例：SQL / Python / 其他语言示例
- 常见错误和注意事项
- 练习题（3-5道）+ 答案解析""",

    "quiz": """## 资源类型要求（习题）
生成一套练习题，包含：
- 选择题（5道）+ 答案
- 简答题（2道）+ 参考答案
- 编程题（1道）+ 参考答案
- 每道题有知识点标注""",

    "ppt": """## 资源类型要求（PPT大纲）
生成 PPT 大纲，包含：
- 封面标题
- 每页标题 + 要点（6-10页）
- 每页备注区内容""",

    "case": """## 资源类型要求（案例材料）
生成一个教学案例，包含：
- 案例背景
- 问题描述
- 分析思路
- 解决方案
- 案例思考题""",

    "review": """## 资源类型要求（复习计划）
生成复习计划，包含：
- 复习目标
- 每日任务安排（3-5天）
- 知识点回顾清单
- 自测题""",

    "test": """## 资源类型要求（阶段测验）
生成阶段测验，包含：
- 选择题（10道）+ 答案
- 判断题（5道）+ 答案
- 简答题（2道）+ 参考答案
- 测验说明（时间、满分、及格线）""",
}

RESOURCE_TYPE_TITLES = {
    "lecture": "知识点讲义",
    "ppt": "PPT大纲",
    "quiz": "习题与答案",
    "case": "案例材料",
    "review": "复习计划",
    "test": "阶段测验",
}


class ResourceGenerationAgent:
    """资源生成智能体"""

    AGENT_NAME = "resource_generation_agent"
    AGENT_DESC = "资源生成智能体 — 生成个性化学习资源"

    def __init__(self, llm_gateway=None):
        self.llm_gateway = llm_gateway

    def run(
        self,
        learning_path: List[Dict[str, Any]],
        resource_type: str,
        difficulty: str,
        student_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """生成学习资源"""
        logger.info(f"[{self.AGENT_NAME}] 生成资源: {resource_type}")

        main_kp = learning_path[0] if learning_path else {}
        kp_name = main_kp.get("kp_name", "知识点")

        path_text = "\n".join(
            f"{i+1}. [{p.get('kp_name', '')}] {p.get('resource_type', '')} | "
            f"预计 {p.get('estimated_time', '')} | 优先级: {p.get('priority', '')}"
            for i, p in enumerate(learning_path)
        ) or "（无学习路径数据）"

        student_info = (
            f"姓名：{student_profile.get('student_name', '未知')}，"
            f"学习目标：{student_profile.get('learning_goal', '暂无')}，"
            f"偏好资源类型：{', '.join(student_profile.get('resource_preferences', [])) or '暂无'}"
        )

        type_instruction = INSTRUCTION_MAP.get(
            resource_type,
            INSTRUCTION_MAP["lecture"]
        )

        messages = [
            {
                "role": "user",
                "content": PROMPT_RESOURCE_GENERATION.format(
                    learning_path=path_text,
                    resource_type=RESOURCE_TYPE_TITLES.get(resource_type, "学习资源"),
                    difficulty=difficulty,
                    student_info=student_info,
                    type_specific_instruction=type_instruction,
                )
            }
        ]

        content = self._call_llm(messages)

        if content is None:
            content = self._generate_content(kp_name, resource_type, difficulty)

        kp_ids = [p.get("kp_id", 0) for p in learning_path]

        return {
            "resource_id": f"res-{uuid.uuid4().hex[:8]}",
            "title": f"{kp_name}专题{RESOURCE_TYPE_TITLES.get(resource_type, '资源')}",
            "type": RESOURCE_TYPE_TITLES.get(resource_type, "学习资源"),
            "knowledge_points": kp_ids,
            "difficulty": difficulty,
            "content": content,
            "target_audience": f"当前学习{difficulty}难度内容",
            "estimated_learning_time": f"约{30 + len(learning_path) * 10}分钟",
            "generation_metadata": {
                "agent": self.AGENT_NAME,
                "model": get_settings().llm_model,
            }
        }

    def _call_llm(self, messages: List[Dict[str, str]]) -> str | None:
        if self.llm_gateway is None:
            return None
        try:
            settings = get_settings()
            config = settings.llm_config()
            config.max_tokens = 4096
            llm_result = self.llm_gateway.generate(messages, config)
            if llm_result.status == "failed":
                logger.error(f"[{self.AGENT_NAME}] LLM 调用失败: {llm_result.error}")
                return None
            logger.info(f"[{self.AGENT_NAME}] LLM 生成完成，{llm_result.output_tokens} tokens")
            return llm_result.content.strip()
        except Exception as e:
            logger.error(f"[{self.AGENT_NAME}] LLM 调用异常: {e}")
        return None

    def _generate_content(self, kp_name: str, resource_type: str, difficulty: str) -> str:
        if resource_type == "lecture":
            return f"""# {kp_name} 专题讲义

## 概述
本讲义帮助学生系统掌握 {kp_name} 相关知识。

## 核心概念
（以下内容由 EduAgent Studio 智能体生成）

### 关键原理
- 原理一：（由智能体生成）
- 原理二：（由智能体生成）

## 实践应用
（以下包含代码示例和案例分析）

### 示例代码
```sql
-- 由智能体生成相关 SQL 语句
SELECT * FROM table WHERE condition;
```

## 练习题
1. （练习题由智能体生成）
2. （练习题由智能体生成）

---
*由 EduAgent Studio 智能体工作台生成*
"""
        elif resource_type == "quiz":
            return f"""# {kp_name} 练习题

## 选择题

**1. 关于 {kp_name}，以下说法正确的是？**
A. 选项A
B. 选项B
C. 选项C
D. 选项D

**答案：** B

**解析：** （由智能体分析）

---
*由 EduAgent Studio 智能体工作台生成*
"""
        else:
            return f"""# {kp_name} 学习资源

（由 EduAgent Studio 智能体工作台生成）

---
*难度：{difficulty}*
"""
