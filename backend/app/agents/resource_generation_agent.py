"""
资源生成智能体

根据学习路径和资源类型生成具体的个性化学习资源。
"""
import logging
import uuid
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ResourceGenerationAgent:
    """资源生成智能体"""

    AGENT_NAME = "resource_generation_agent"
    AGENT_DESC = "资源生成智能体 — 生成个性化学习资源"

    RESOURCE_TYPE_TITLES = {
        "lecture": "知识点讲义",
        "ppt": "PPT大纲",
        "quiz": "习题与答案",
        "case": "案例材料",
        "review": "复习计划",
        "test": "阶段测验",
    }

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
        kp_ids = [p.get("kp_id", 0) for p in learning_path]

        title = f"{kp_name}专题{'讲义' if resource_type == 'lecture' else '资源'}（{difficulty}）"
        content = self._generate_content(kp_name, resource_type, difficulty)

        return {
            "resource_id": f"res-{uuid.uuid4().hex[:8]}",
            "title": title,
            "type": self.RESOURCE_TYPE_TITLES.get(resource_type, "学习资源"),
            "knowledge_points": kp_ids,
            "difficulty": difficulty,
            "content": content,
            "target_audience": f"已掌握基础的学生，当前学习{difficulty}难度",
            "estimated_learning_time": f"约{30 + len(learning_path) * 10}分钟",
            "generation_metadata": {
                "agent": self.AGENT_NAME,
                "model": "mock-gpt",
            }
        }

    def _generate_content(self, kp_name: str, resource_type: str, difficulty: str) -> str:
        if resource_type == "lecture":
            return f"""# {kp_name} 专题讲义

## 概述
本讲义帮助学生系统掌握 {kp_name} 相关知识。

## 核心概念
（详细内容由智能体根据学习路径生成）

### 关键原理
- 原理一：（由智能体生成）
- 原理二：（由智能体生成）

## 实践应用
（包含代码示例和案例分析）

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
