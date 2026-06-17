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

    "mindmap": """## 资源类型要求（思维导图）
生成知识点的思维导图，以 Markdown 树形结构呈现，包含：
- 中心主题：知识点名称
- 一级分支：核心概念（3-5个）
- 二级分支：每个概念的关键要点
- 末级分支：具体示例或注意事项
- 整体结构层次分明，便于学生建立知识体系""",

    "code_case": """## 资源类型要求（代码实操案例）
生成一个完整的代码实操案例，包含：
- 案例目标：解决什么实际问题
- 需求描述：清晰的功能需求
- 代码实现：完整可运行的代码（Python/SQL/Java等）
- 运行结果：代码执行后的输出示例
- 关键讲解：代码中核心逻辑的解释
- 拓展练习：2-3道改编题""",

    "video_script": """## 资源类型要求（视频/动画脚本）
生成一个教学视频/动画脚本，包含：
- 视频标题和时长建议（3-5分钟）
- 分镜脚本：每段的文字内容、动画描述、时长
- 讲解旁白：配合每段画面的讲解词
- 视觉素材提示：需要展示的图表、代码、动画
- 互动问题：视频中设置的思考题""",

    "experiment_report": """## 资源类型要求（实验报告）
生成一份实验报告模板，包含：
- 实验目的：本次实验要掌握的知识点
- 实验环境：所需工具、环境配置
- 实验步骤：详细操作流程（分步骤）
- 预期结果：每个步骤的预期输出
- 结果分析：如何分析实验结果
- 常见问题与解决：实验中的典型问题
- 思考题：2-3道延伸思考""",

    "error_analysis": """## 资源类型要求（错题解析）
生成常见错误分析文档，包含：
- 错误类型分类（如：概念混淆、计算错误、审题失误）
- 每类错误的典型例题（含错误做法和正确做法）
- 错误原因剖析：为什么容易犯这个错
- 正确做法讲解：如何避免
- 配套练习：同类题目的变式练习""",

    "learning_card": """## 资源类型要求（学习卡片）
生成一组知识速记卡片（5-8张），每张卡片包含：
- 卡片标题：一个核心概念/公式/术语
- 正面：概念名称 + 简短定义
- 背面：详细解释 + 示例 + 记忆口诀
- 适合课间快速记忆和复习""",
}

RESOURCE_TYPE_TITLES = {
    "lecture": "知识点讲义",
    "ppt": "PPT大纲",
    "quiz": "习题与答案",
    "case": "案例材料",
    "review": "复习计划",
    "test": "阶段测验",
    "mindmap": "思维导图",
    "code_case": "代码实操案例",
    "video_script": "视频/动画脚本",
    "experiment_report": "实验报告",
    "error_analysis": "错题解析",
    "learning_card": "学习卡片",
}

# 防幻觉检测 prompt — 对比生成内容与知识库上下文，标记矛盾点
PROMPT_HALLUCINATION_CHECK = """你是一个严格的知识质量审查智能体。请对比以下「课程知识库」和「生成内容」，检查是否存在事实性错误或幻觉。

## 课程知识库（权威来源）
{context}

## 生成内容（待审查）
{content}

## 审查要求
请检查以下几类问题：
1. **事实性错误**：知识库中明确否定或与事实不符的陈述
2. **概念混淆**：将不同知识点的概念混用
3. **过时信息**：知识库有更新版本但生成内容仍用旧版本
4. **代码错误**：SQL/Python 代码与知识库描述的行为不一致
5. **超纲内容**：超出知识库范围且未标注"进阶内容"

请以 JSON 格式输出审查结果：
{{
  "has_hallucination": true/false,
  "warnings": [
    {{"type": "事实性错误", "location": "第2段第3句", "claim": "具体错误陈述", "correction": "正确陈述"}},
    ...
  ],
  "summary": "一句话总结"
}}

要求：
- has_hallucination: 存在任何事实性错误时为 true
- warnings: 列出所有发现的问题，无问题时为空数组 []
- 每条 warning 需包含 type/location/claim/correction
- 只输出 JSON，不要有其他内容
"""


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
        kp_id_str = ",".join(str(kid) for kid in kp_ids if kid) if kp_ids else ""

        # === 防幻觉检测 ===
        hallucination_warnings = []
        rag_context = self._retrieve_rag_for_check(kp_name, kp_ids)
        if rag_context and content and len(content) > 100:
            check_result = self._hallucination_check(content, rag_context)
            if check_result:
                hallucination_warnings = check_result.get("warnings", [])
                logger.info(f"[{self.AGENT_NAME}] 幻觉检测完成: {len(hallucination_warnings)} 个警告")

        return {
            "resource_id": f"res-{uuid.uuid4().hex[:8]}",
            "title": f"{kp_name}专题{RESOURCE_TYPE_TITLES.get(resource_type, '资源')}",
            "type": RESOURCE_TYPE_TITLES.get(resource_type, "学习资源"),
            "target_kp_ids": kp_id_str,
            "knowledge_points": kp_ids,
            "difficulty": difficulty,
            "content": content,
            "target_audience": f"当前学习{difficulty}难度内容",
            "estimated_learning_time": f"约{30 + len(learning_path) * 10}分钟",
            "generation_metadata": {
                "agent": self.AGENT_NAME,
                "model": get_settings().llm_model,
            },
            "hallucination_warnings": hallucination_warnings,
        }

    def _retrieve_rag_for_check(
        self,
        kp_name: str,
        kp_ids: List[int],
    ) -> str:
        """为幻觉检测检索课程知识库上下文"""
        try:
            from app.services.rag_service import get_context_for_agent
            query = kp_name or "课程知识点"
            context = get_context_for_agent(query=query, top_k=5)
            return context if context else ""
        except Exception as e:
            logger.warning(f"[{self.AGENT_NAME}] RAG 检索失败，跳过幻觉检测: {e}")
            return ""

    def _hallucination_check(self, content: str, rag_context: str) -> Dict[str, Any] | None:
        """对比生成内容与知识库，检测幻觉"""
        import json
        messages = [
            {
                "role": "user",
                "content": PROMPT_HALLUCINATION_CHECK.format(
                    context=rag_context or "（无知识库上下文）",
                    content=content[:2000],
                )
            }
        ]
        try:
            settings = get_settings()
            config = settings.llm_config()
            config.max_tokens = 1024
            llm_result = self.llm_gateway.generate(messages, config)
            if llm_result.status == "failed":
                logger.warning(f"[{self.AGENT_NAME}] 幻觉检测 LLM 调用失败: {llm_result.error}")
                return None
            raw = llm_result.content.strip()
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw = "\n".join(lines[1:] if lines[0].startswith("```json") else lines)
                raw = raw.replace("```", "").strip()
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"[{self.AGENT_NAME}] 幻觉检测 JSON 解析失败: {e}")
        except Exception as e:
            logger.warning(f"[{self.AGENT_NAME}] 幻觉检测异常: {e}")
        return None

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
