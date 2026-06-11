"""
提示词模板导入脚本
database/08_insert_prompt_templates.sql 配套 Python 执行脚本

功能：向 prompt_templates 和 prompt_versions 表中导入高质量提示词模板。
用法：python import_prompts.py
依赖：pip install pymysql
"""
import pymysql
import sys

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="061202",
    database="ai_collab_audit_system",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False,
)
cursor = conn.cursor()

# ── 模板数据 ────────────────────────────────────────────────────────────────
# (template_name, task_type_id, description, version_no(int), prompt_content, change_note)
TEMPLATES = [
    # 分类一：项目管理 (task_type_id=1)
    ("项目需求分析生成", 1,
     "根据项目背景和目标，生成结构化的需求分析文档初稿，支持多级功能点枚举和非功能需求描述。",
     1,
"""## 任务
你是一名经验丰富的高校项目需求分析师。请根据以下信息，为项目生成一份完整的《需求规格说明书》初稿。

## 项目信息
- 项目名称：{{project_name}}
- 项目背景：{{project_background}}
- 主要目标：{{project_goals}}
- 目标用户：{{target_users}}
- 约束条件：{{constraints}}

## 输出要求
请生成包含以下章节的 Markdown 文档：
1. **引言**（目的、范围、定义、参考资料）
2. **总体描述**（产品视角、用户特征、假设与依赖）
3. **功能需求**（按优先级枚举，每个功能点包含：功能编号、名称、描述、输入/输出、约束）
4. **非功能需求**（性能、安全、可靠性、可用性、可维护性）
5. **接口需求**（用户接口、硬件接口、软件接口、通信接口）
6. **数据需求**（逻辑数据模型，主要数据实体及关系）

## 格式要求
- 功能点编号格式：A-1, A-2, B-1 ...（按模块分层）
- 每个功能点描述不超过 150 字
- 非功能需求须给出量化指标（如响应时间 < 3s）

## 补充上下文
{{additional_context}}""",
     "自主设计，v1：初始版本，覆盖高校项目协作场景完整章节结构"),

    ("敏捷用户故事生成", 1,
     "将功能需求列表转换为符合敏捷规范的用户故事（Epic / User Story / Acceptance Criteria）。",
     1,
"""## 任务
你是一名 Scrum Master。请将以下功能需求列表转换为敏捷用户故事体系。

## 项目信息
- 项目名称：{{project_name}}
- 开发周期：{{sprint_duration}}
- 团队规模：{{team_size}} 人

## 功能需求列表
{{feature_list}}

## 输出要求
请以表格形式输出：

| 编号 | 类型 | 标题 | 描述（As a... I want... So that...） | 验收标准（Given/When/Then） | 优先级 | 估算故事点 |
|------|------|------|-------------------------------------|---------------------------|--------|-----------|

## 规则
- Epic 用粗体标记，Story 用普通文本
- 每个 Story 必须包含完整的验收标准（至少 2 条）
- 优先级：P0=必须做，P1=应该做，P2=可以做
- 故事点估算采用斐波那契数列（1, 2, 3, 5, 8, 13）
- 将故事分配到以下冲刺：{{sprint_assignments}}

## 补充说明
{{additional_context}}""",
     "自主设计，v1：输出符合敏捷规范的 Epic/Story/AC 结构"),

    ("毕业设计开题报告生成", 1,
     "根据研究方向和初步想法，生成完整的本科/硕士毕业设计开题报告。",
     1,
"""## 任务
你是一名毕业设计指导教师。请根据以下信息，帮助学生生成一份完整的开题报告。

## 学生信息
- 姓名：{{student_name}} | 学号：{{student_no}} | 专业：{{major}} | 指导教师：{{supervisor_name}}

## 研究主题
- 论文题目：{{thesis_title}}
- 关键词：{{keywords}}
- 研究方向：{{research_direction}}

## 研究背景与意义
{{research_background}}

## 国内外研究现状
{{literature_review}}

## 研究目标与内容
### 研究目标
{{research_objectives}}

### 研究内容
{{research_content}}

## 研究方案
### 拟采用的研究方法
{{research_methods}}

### 技术路线
请用文字描述主要技术路线步骤（配合 Mermaid 流程图）。

### 可行性分析
- 理论可行性：{{theoretical_feasibility}}
- 技术可行性：{{technical_feasibility}}
- 时间可行性：{{timeline_feasibility}}

## 研究计划
| 阶段 | 时间 | 主要工作 | 预期成果 |
|------|------|---------|---------|

## 参考文献
{{references}}

## 输出要求
生成完整开题报告 Markdown 文档，包含：课题背景与意义、国内外研究现状、研究目标与内容、研究方案与技术路线、可行性分析、研究计划、参考文献。

## 写作要求
- 严禁虚构不存在的文献
- 研究意义须从"理论价值"和"实际应用"两个角度展开
- 技术路线须清晰可执行

## 补充说明
{{additional_context}}""",
     "自主设计，v1：适用于高校计算机类本科/硕士毕业设计开题报告"),

    ("需求变更影响分析", 1,
     "分析需求变更对现有系统功能、数据模型和测试用例的影响范围，给出实施建议。",
     1,
"""## 任务
你是一名需求变更分析师。请分析以下需求变更对项目的影响范围，并给出实施建议。

## 项目信息
- 项目名称：{{project_name}}
- 当前阶段：{{project_phase}}（需求分析 / 开发中 / 测试中 / 已上线）
- 原计划交付时间：{{original_deadline}}

## 需求变更描述
{{change_description}}

## 变更原因
{{change_reason}}

## 变更紧急程度
{{change_urgency}}（必须做 / 尽快做 / 可以放到下一版）

## 当前系统状态
- 已完成功能：{{completed_features}}
- 进行中功能：{{in_progress_features}}
- 未开始功能：{{planned_features}}

## 影响分析维度

### 1. 功能影响
- 受影响的功能模块：{{affected_modules}}
- 影响程度：{{impact_level}}（高/中/低）
- 是否影响已上线功能：{{affects_production}}

### 2. 数据影响
- 数据模型变更：{{data_model_changes}}
- 数据迁移需求：{{data_migration_needs}}
- 历史数据兼容处理：{{backward_compatibility}}

### 3. 接口影响
- 受影响的 API 端点：{{affected_apis}}
- 是否有 API 兼容性破坏：{{api_breaking_change}}

### 4. 测试影响
- 受影响测试用例数量：{{affected_test_cases}}
- 需新增测试用例：{{new_test_cases_needed}}

### 5. 文档影响
- 需更新的文档：{{docs_to_update}}

## 输出要求

### 变更可行性评估
[ ] 可行，建议接受  [ ] 可行，需调整范围  [ ] 风险较高  [ ] 建议拒绝（理由：{{rejection_reasons}}）

### 影响范围矩阵
| 影响项 | 当前状态 | 变更后状态 | 影响模块 | 影响程度 | 修复方案 |
|-------|---------|----------|---------|---------|---------|

### 工作量估算
- 开发：{{dev_effort}} 人天 | 测试：{{qa_effort}} 人天 | 文档：{{doc_effort}} 人天 | 总计：{{total_effort}} 人天

### 实施建议
- 建议实施方式：{{implementation_approach}}
- 建议实施时间：{{recommended_timeline}}
- 风险缓解措施：{{risk_mitigation}}

## 补充说明
{{additional_context}}""",
     "自主设计，v1：用于系统化评估需求变更的范围和实施风险"),

    ("项目组会议纪要生成", 1,
     "根据会议信息和讨论要点，生成结构化、可追溯的项目会议纪要。",
     1,
"""## 任务
你是一名项目管理秘书。请根据以下会议信息，生成结构化的会议纪要。

## 会议基本信息
- 项目名称：{{project_name}}
- 会议主题：{{meeting_topic}}
- 会议时间：{{meeting_time}}
- 主持人：{{host_name}} | 记录人：{{note_taker}}
- 参会人员：{{attendees}}

## 会议议程
{{meeting_agenda}}

## 讨论内容摘要
{{discussion_summary}}

## 决议事项（Action Items）
{{decisions_made}}

## 待解决问题
{{open_issues}}

## 输出格式

### 会议基本信息表
| 字段 | 内容 |
|------|------|

### 议程执行情况
| 议题 | 讨论时长 | 结论 |
|------|---------|------|

### 决议清单
| # | 决议内容 | 负责人 | 完成时限 | 优先级 |
|---|---------|-------|---------|-------|

### 风险与阻塞
| 问题描述 | 影响评估 | 建议对策 | 责任人 |

### 下次会议安排
- 时间：{{next_meeting_time}}
- 主题：{{next_meeting_topic}}
- 准备事项：{{preparation_items}}

## 格式要求
- Markdown 格式，结构清晰
- 关键决议用加粗标记
- 会议纪要须在会议结束后 24 小时内发出

## 补充说明
{{additional_context}}""",
     "自主设计，v1：适用于高校项目组的定期同步和专题讨论会议"),

    ("AI 提示词质量评审与优化", 1,
     "对已有提示词进行系统性质量评审，给出清晰度、完整性、约束条件和示例优化建议。",
     1,
"""## 任务
你是一名提示词工程专家（Prompt Engineer）。请对以下提示词进行系统性质量评审，并给出优化建议。

## 待评审提示词
```
{{original_prompt}}
```

## 使用场景
- 应用场景：{{use_case}}
- 目标 AI 模型：{{target_model}}
- 期望输出格式：{{expected_output_format}}
- 当前遇到的问题（如有）：{{current_issues}}

## 评审维度
1. **角色定义**：是否有明确角色设定？角色背景是否足够专业？
2. **任务描述**：任务目标是否清晰无歧义？输出要求是否完整（格式/长度/风格）？
3. **输入变量**：变量是否完整覆盖所需信息？命名是否清晰？
4. **约束条件**：是否明确排除了不需要的内容？是否限制了输出范围？
5. **示例（Few-shot）**：是否提供了高质量的输入-输出示例？覆盖了边界情况？

## 输出格式

### 综合评分（1-10 分）
| 维度 | 得分 | 满分 | 主要问题 |
|------|------|------|---------|

### 问题清单
| # | 维度 | 问题描述 | 改进建议 |
|---|-----|---------|---------|

### 优化后的提示词
请提供改进版本。

### 优化说明
简要说明最重要的 3 条优化及其预期效果。

## 补充说明
{{additional_context}}""",
     "自主设计，v1：用于对系统内其他提示词模板进行质量评审和迭代优化"),

    ("AI 辅助课程报告生成", 1,
     "根据项目概述和任务要求，生成结构完整、格式规范的课程报告章节内容。",
     1,
"""## 任务
你是一名高校课程助教。请根据以下信息，生成课程报告的指定章节内容。

## 项目信息
- 课程名称：{{course_name}}
- 项目名称：{{project_name}}
- 章节要求：{{chapter_requirement}}
- 总字数要求：约 {{word_count}} 字

## 项目背景
{{project_background}}

## 技术栈
{{tech_stack}}

## 具体要求
{{specific_requirements}}

## 参考资料
{{reference_materials}}

## 输出要求
### 格式规范
- 标题层级：## 二级标题，### 三级标题
- 代码块使用 ```语言 标记
- 表格使用 Markdown 表格语法
- 引用使用 > 块引用格式

### 内容要求
- 论述需有论点、论据、论证过程
- 结合项目实际数据/截图说明（如有）
- 避免空洞套话，每段需有实质内容
- 字数需达到要求下限，可超出 10%

### 章节结构
{{chapter_structure_template}}

## 补充说明
{{additional_context}}""",
     "自主设计，v1：适用于各类高校计算机/软件课程报告生成"),

    # 分类二：数据库课程设计 (task_type_id=2)
    ("数据库概念设计生成", 2,
     "根据业务描述生成 E-R 图实体关系描述和规范化分析建议。",
     1,
"""## 任务
你是一名数据库架构师。请根据以下业务描述，生成数据库概念设计（ER 图）说明。

## 项目信息
- 项目名称：{{project_name}}
- 业务背景：{{business_background}}

## 业务需求描述
{{business_requirements}}

## 业务规则
{{business_rules}}

## 输出要求

### 1. 实体清单
| 实体名 | 英文名 | 主要属性 | 实体说明 |
|--------|--------|---------|---------|

### 2. 关系描述（Chen 记号）
- 1:N 关系示例：学生（Student）与管理关系（Manage）为 1:N，描述：一名教师可管理多名学生。
- N:M 关系示例：课程（Course）与选课关系（Enroll）为 N:M，描述：一名学生可选修多门课程。

### 3. 属性映射
为每个实体列出关键属性（含主键 PK，外键 FK）。

### 4. 规范化分析
分析各实体当前范式级别（1NF/2NF/3NF/BCNF），指出可能存在的更新异常，并给出分解建议。

### 5. 约束条件
列出数据完整性约束：NOT NULL、UNIQUE、CHECK、参照完整性等。

## 补充说明
{{additional_context}}""",
     "自主设计，v1：覆盖高校数据库课程设计核心需求"),

    ("MySQL DDL 建表语句生成", 2,
     "根据 ER 图描述或需求说明，生成符合 MySQL 8.0 的完整 DDL 建表语句，包含索引、外键和注释。",
     1,
"""## 任务
你是一名 MySQL 数据库工程师。请根据以下数据库设计说明，生成完整的 MySQL 8.0 DDL 建表语句。

## 项目信息
- 项目名称：{{project_name}}
- 数据库名：{{db_name}}

## 实体设计说明
{{entity_design}}

## 设计要求
- 存储引擎：InnoDB
- 字符集：utf8mb4，排序规则：utf8mb4_unicode_ci
- 主键优先使用自增 BIGINT UNSIGNED
- 所有表必须添加中文 COMMENT 注释
- 外键约束需注明 ON DELETE / ON UPDATE 行为
- 需为高频查询字段建立合适索引

## 输出要求
请生成完整的 CREATE TABLE 语句，包含：表结构（字段/类型/约束/注释）、所有索引、所有外键约束、表级 COMMENT。

## 示例格式
```sql
CREATE TABLE `表名` (
    `字段名` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '字段中文注释',
    PRIMARY KEY (`字段名`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表中文注释';
```

## 补充说明
{{additional_context}}""",
     "自主设计，v1：输出符合 MySQL 8.0 规范的生产级 DDL"),

    ("数据库课程设计报告生成", 2,
     "根据项目信息、ER图和DDL，生成完整的数据库课程设计报告文档。",
     1,
"""## 任务
你是一名数据库课程教师。请根据以下材料，生成一份完整的《数据库课程设计报告》。

## 项目信息
- 项目名称：{{project_name}}
- 开发工具：{{dev_tools}}
- 数据库版本：{{db_version}}

## ER 图描述
{{er_diagram}}

## DDL 语句
{{ddl_statements}}

## 业务背景
{{business_background}}

## 输出要求
报告须包含以下章节：

### 第1章 需求分析
- 业务功能描述
- 数据需求分析
- 功能模块划分

### 第2章 概念设计
- ER 图（含实体、属性、关系描述）
- 各实体的属性及键（主键，外键）

### 第3章 逻辑设计
- ER 图转换为关系模型
- 关系模式（含码的分析）
- 规范化分析（各关系达到的范式级别）

### 第4章 物理设计
- MySQL DDL 完整建表语句
- 索引设计说明
- 存储参数设置

### 第5章 数据库实现
- 主要建表语句（含注释）
- 典型查询示例（至少 5 条，含触发器/存储过程）

### 第6章 总结与反思
- 设计亮点
- 不足与改进方向

## 格式要求
- Markdown 格式，约 3000-5000 字
- 代码块使用 ```sql 标记
- 表格使用 Markdown 表格语法

## 补充说明
{{additional_context}}""",
     "自主设计，v1：覆盖高校数据库课程设计报告全部章节"),

    # 分类三：SQL 代码解释 (task_type_id=3)
    ("AI 生成代码质量审核", 3,
     "对 AI 生成的代码进行多维度质量评分和审核，适用于代码提交前的质量把关。",
     1,
"""## 任务
你是一名 AI 代码质量审计员。请对以下 AI 生成的代码进行系统性质量审核和评分。

## 审核背景
- 项目名称：{{project_name}}
- 任务/模块：{{task_title}}
- 原始需求：{{original_requirement}}
- AI 模型：{{ai_model_name}}
- 编程语言：{{programming_language}}

## AI 生成代码
```
{{ai_generated_code}}
```

## 审核标准（每项 1-10 分）
| 审核维度 | 说明 | 权重 | 评分 | 扣分原因 |
|---------|------|------|------|---------|
| 功能正确性 | 代码是否完整满足原始需求 | 25% | | |
| 语法正确性 | 语言语法是否完全正确 | 15% | | |
| 逻辑严谨性 | 边界条件、异常处理是否完整 | 20% | | |
| 性能效率 | 算法复杂度、查询效率是否合理 | 15% | | |
| 安全合规性 | 是否有注入、硬编码密码等安全隐患 | 15% | | |
| 可读性与维护性 | 命名规范、注释清晰、结构合理 | 10% | | |

## 输出要求

### 总体评分
综合加权得分：__/10 分
评级：[ ] 优秀（9-10）[ ] 良好（7-8）[ ] 及格（5-6）[ ] 较差（<5）

### 问题清单
| 序号 | 严重程度 | 代码位置 | 问题描述 | 修复建议 |
|------|---------|---------|---------|---------|
严重程度：Critical（必须修改）/ Warning（建议修改）/ Suggestion（可选优化）

### 审核结论
[ ] 可直接采纳
[ ] 需修改后采纳（附必改清单）
[ ] 建议重做

## 补充说明
{{additional_context}}""",
     "自主设计，v1：用于对 AI 生成代码进行多维度质量把关和评分"),

    ("SQL 查询质量审核", 3,
     "对 AI 生成的 SQL 查询进行正确性、性能和安全审核，适用于数据库课程作业和项目开发。",
     1,
"""## 任务
你是一名数据库性能工程师。请对以下 SQL 查询进行系统性审核。

## 审核背景
- 项目名称：{{project_name}}
- 查询目的：{{query_purpose}}
- 数据库类型：{{db_type}}（MySQL / PostgreSQL / SQL Server）

## 待审核 SQL
```sql
{{sql_query}}
```

## 数据库 schema（如适用）
{{schema_info}}

## 审核维度

### 1. 功能正确性
- 查询是否完整覆盖需求？
- JOIN 条件是否正确（笛卡尔积风险）？
- WHERE 条件是否会产生意外空值判断？

### 2. 性能分析
- 索引使用情况（是否利用了已有索引？）
- 全表扫描风险评估
- 预估时间复杂度

### 3. 安全审核
- 是否有 SQL 注入风险？
- 是否暴露了不必要的敏感字段？

### 4. 代码规范
- 关键字大小写是否规范？
- 别名命名是否清晰（禁止 a, b, t1 等无意义别名）？

## 输出格式

### 综合评级
[ ] 优秀 [ ] 良好 [ ] 及格 [ ] 较差

### 问题清单
| # | 严重程度 | 维度 | 问题描述 | 改进 SQL（如适用） |
|---|-------|------|---------|-----------------|

### 优化后的 SQL
请提供改进后的完整 SQL（可选）。

## 补充说明
{{additional_context}}""",
     "自主设计，v1：专注 SQL 查询正确性、性能和安全审核"),

    ("Python REST API CRUD 生成", 3,
     "根据数据库表结构和业务需求，生成符合 RESTful 规范的后端 CRUD API 代码（Python Flask/FastAPI）。",
     1,
"""## 任务
你是一名 Python 后端工程师。请根据以下信息，生成符合 RESTful 规范的后端 CRUD API 代码。

## 技术栈
- 框架：{{framework}}（Flask / FastAPI）
- ORM：{{orm}}（SQLAlchemy / Peewee）
- 数据库：{{db_type}}
- 认证方式：{{auth_method}}（JWT / Session / 无）

## 业务信息
- 模块名称：{{module_name}}
- 模块中文名：{{module_cn_name}}

## 数据库表结构
```sql
{{table_schema}}
```

## API 需求
{{api_requirements}}

## 业务规则
{{business_rules}}

## 输出要求

### 1. 数据模型（Model）
```python
# app/models/{{module_name}}.py
```

### 2. Schema 定义（用于请求验证和响应序列化）
使用 Pydantic（FastAPI）或 Marshmallow（Flask）

### 3. CRUD API 路由
```python
# app/routers/{{module_name}}.py
# 实现：GET列表/POST创建/GET详情/PUT更新/DELETE删除（软删除）
```

### 4. 路由注册
```python
# app/main.py 中的路由注册代码片段
```

## 代码规范
- 遵循 PEP 8 规范
- 所有函数须有中文 DocString
- 使用类型注解（type hints）
- 敏感操作须记录操作日志
- 统一错误响应格式：{code: int, message: str, data: any}

## 补充说明
{{additional_context}}""",
     "自主设计，v1：输出符合 RESTful 规范和项目架构的 Python CRUD API"),

    ("复杂 SQL 查询生成", 3,
     "根据自然语言查询需求，生成正确、高效的多表关联 SQL 查询语句。",
     1,
"""## 任务
你是一名 SQL 专家。请根据以下查询需求，生成正确的 SQL 语句。

## 数据库信息
- 数据库类型：{{db_type}}（MySQL 8.0 / PostgreSQL 14 / SQL Server 2019）
- 表结构说明：
```sql
{{schema_info}}
```

## 查询需求（自然语言）
{{query_requirement}}

## 查询要求说明
- 输出记录数：{{output_limit}}
- 是否需要分页：{{need_pagination}}
- 是否需要总计/小计：{{need_aggregation}}
- 结果排序：{{sort_order}}

## 输出要求

### 1. SQL 查询语句
```sql
-- 查询目的：{{query_purpose}}
{{generated_sql}}
```

### 2. 语句说明
- 核心逻辑：{{logic_explanation}}
- 关键 JOIN 说明：{{join_explanation}}
- 索引优化建议：{{index_suggestions}}

### 3. 查询计划分析（文字描述）
- 是否走全表扫描：{{full_scan_risk}}
- 预估时间复杂度：{{complexity}}
- 优化建议：{{optimization_tips}}

### 4. 示例输出
如查询结果为表格，请给出前 5 行示例数据：
| 字段1 | 字段2 | ... |

## SQL 编码规范
- 关键字大写：SELECT, FROM, WHERE, JOIN ...
- 字段别名用 AS，清晰可读
- 子查询须有注释说明其作用
- 避免 SELECT *，明确列出需要的字段

## 补充说明
{{additional_context}}""",
     "自主设计，v1：支持多数据库方言的复杂 SQL 查询生成"),

    ("RESTful API 文档生成", 3,
     "根据业务需求描述，生成符合 OpenAPI 3.0 规范的 API 接口文档（YAML 格式）。",
     1,
"""## 任务
你是一名 API 架构师。请根据以下业务需求描述，生成符合 OpenAPI 3.0 规范的 API 接口文档。

## 项目信息
- 项目名称：{{project_name}}
- API 版本：{{api_version}}（v1 / v2）
- Base URL：{{base_url}}
- 认证方式：{{auth_method}}（Bearer JWT / API Key / OAuth 2.0）

## 业务模块
{{business_modules}}

## API 需求说明
{{api_requirements}}

## 输出要求
请生成完整的 OpenAPI 3.0 YAML 文档：

```yaml
openapi: 3.0.3
info:
  title: {{api_title}}
  version: {{api_version}}
  description: {{api_description}}
servers:
  - url: {{base_url}}
paths:
  # 每个端点的详细定义
components:
  securitySchemes:
  schemas:        # 数据模型定义
  responses:      # 通用响应定义
tags:
```

### 每个 API 端点须包含
- HTTP 方法（GET/POST/PUT/DELETE）
- 操作 ID（operationId）、摘要（summary）和描述（description）
- 请求参数（path / query / header / body）
- 请求体 Schema（JSON Schema 格式）
- 响应定义（200 / 400 / 401 / 403 / 404 / 500）
- 安全要求（security）

### 数据模型（components/schemas）
- 每个主要实体须有完整的 Schema 定义
- 须包含所有字段的类型、格式、描述
- 须定义必填字段（required）
- 须有中文 description

## 规范要求
- 遵循 RESTful 设计原则
- 资源命名用复数名词（/users, /projects）
- HTTP 状态码正确（GET->200, POST->201, DELETE->204）

## 补充说明
{{additional_context}}""",
     "自主设计，v1：生成符合 OpenAPI 3.0 规范的完整 RESTful API 文档"),

    # 分类四：代码注释生成 (task_type_id=9)
    ("代码审查意见生成", 9,
     "对提交的代码进行系统性审查，输出结构化的审查报告，包括问题分级和改进建议。",
     1,
"""## 任务
你是一名资深代码审查工程师（Code Reviewer）。请对以下代码提交进行系统性审查，并生成结构化审查报告。

## 项目信息
- 项目名称：{{project_name}}
- 任务/模块：{{task_title}}
- 编程语言：{{programming_language}}
- 代码提交类型：{{change_type}}（新增 / 修改 / 重构 / Bug 修复）

## 待审查代码
```
{{code_snippet}}
```

## 审查范围要求
1）正确性：逻辑是否正确处理边界条件和异常？
2）安全性：是否有注入、越权等安全漏洞？
3）性能：是否有 N+1 查询、内存泄漏风险？
4）可维护性：命名是否清晰、函数是否过长、是否违反 SOLID？
5）代码规范：是否遵循语言/项目编码规范？
6）测试覆盖：关键逻辑是否有对应单元测试？
7）文档注释：公共 API 是否添加了必要的注释？

## 输出格式

### 审查结论
[ ] 通过，建议合并
[ ] 需要修改后合并（列出必改项）
[ ] 拒绝（存在严重问题）

### 问题清单
| 序号 | 严重程度 | 代码位置 | 问题描述 | 修复建议 |
|------|---------|---------|---------|---------|
严重程度：Critical（必须修改）/ Warning（建议修改）/ Suggestion（可选优化）

### 总体评价
- 优点：{{strengths}}
- 核心风险：{{core_risks}}
- 改进优先级：{{improvement_priority}}

## 补充说明
{{additional_context}}""",
     "自主设计，v1：输出符合工程实践的结构化代码审查报告"),

    ("函数级代码注释生成", 9,
     "为指定函数或存储过程生成规范的 JSDoc / DocString / SQL 注释，包括参数说明、返回值和异常说明。",
     1,
"""## 任务
你是一名代码文档工程师。请为以下代码片段生成规范的函数级注释。

## 代码语言
{{programming_language}}（支持：Python / Java / JavaScript / SQL / C）

## 代码片段
```
{{code_snippet}}
```

## 上下文
- 项目名称：{{project_name}}
- 模块/包：{{module_name}}
- 函数预期用途：{{function_purpose}}
- 调用者角色：{{caller_role}}（前端 / 后端服务 / 定时任务 / 存储过程调用）
- 是否为公共 API：{{is_public_api}}（是/否）

## 输出要求

### Python -> Google Style Docstring
```python
def function_name(param1: type, param2: type) -> return_type:
    \"\"\"一句话功能描述。

    详细描述函数的工作原理（超过一行时）。

    Args:
        param1 (type): 参数说明，包含有效值范围和默认值。
        param2 (type): 参数说明。

    Returns:
        return_type: 返回值说明。

    Raises:
        ExceptionType: 何时抛出此异常。

    Examples:
        >>> function_name("input", 123)
        {"result": "..."}
    \"\"\"
```

### Java -> Javadoc
### SQL -> 块注释（--）格式

## 规则
- 注释内容须准确描述代码实际行为，禁止臆测
- 参数描述须包含类型、含义、约束（如：非空 / 取值范围）
- 返回值描述须区分正常返回和异常返回
- Examples 部分须包含至少一个可用示例

## 补充说明
{{additional_context}}""",
     "自主设计，v1：支持 Python/Java/JavaScript/SQL 多语言注释生成"),

    ("Python 单元测试用例生成", 9,
     "根据 Python 函数签名和文档字符串，生成符合 pytest 规范的单元测试用例，覆盖正常路径和边界条件。",
     1,
"""## 任务
你是一名测试工程师。请根据以下 Python 函数，生成符合 pytest 规范的完整单元测试用例。

## 项目信息
- 项目名称：{{project_name}}
- 测试框架：{{test_framework}}（pytest / unittest）
- 测试覆盖率目标：{{coverage_target}}%

## 待测试函数
```python
{{function_code}}
```

## 函数使用说明
- 函数功能：{{function_purpose}}
- 调用场景：{{calling_scenarios}}
- 已知约束：{{constraints}}

## 输出要求

### 1. 测试文件头部
```python
# tests/test_{{module_name}}.py
import pytest
from app.{{module_name}} import {{function_name}}
```

### 2. 测试用例要求
- **正常路径测试**：至少 3 个，覆盖典型输入和预期输出
- **边界条件测试**：空值/None 输入、边界数值、非法类型、空字符串/空列表/空字典
- **异常测试**：使用 pytest.raises 验证异常抛出
- **参数化测试**：使用 @pytest.mark.parametrize 合并相似测试

### 3. 测试用例命名
遵循 test_{{function_name}}_{{scenario}}_{{expected}} 命名规范

## 代码规范
- 每条断言须有清晰的错误信息（assert actual == expected, f"期望 {expected}，实际 {actual}"）
- 使用 pytest fixtures 管理测试数据
- 测试用例之间相互独立，无执行顺序依赖

## 补充说明
{{additional_context}}""",
     "自主设计，v1：生成覆盖正常路径和边界条件的 pytest 单元测试"),

    # 分类五：文献综述撰写 (task_type_id=5)
    ("文献综述章节生成", 5,
     "根据给定关键词和研究方向，生成结构化的文献综述章节，综述该领域的研究现状与发展趋势。",
     1,
"""## 任务
你是一名学术研究员。请为以下研究主题撰写文献综述章节。

## 研究信息
- 研究主题：{{research_topic}}
- 研究方向：{{research_direction}}
- 章节字数：约 {{word_count}} 字
- 引用文献数量：不少于 {{min_citations}} 篇

## 研究背景
{{research_background}}

## 已有文献信息
{{existing_literature}}

## 输出要求

### 1. 研究背景与意义
（2-3 段，交代研究背景、现有研究空白、本研究的重要性）

### 2. 国内外研究现状
（按子方向/方法论分类综述，每类：主流方法及代表作者/年份、各方法优缺点对比表格、当前最佳性能指标）

### 3. 技术路线对比
| 方法 | 核心思想 | 代表工作 | 优点 | 缺点/局限 |
|------|---------|---------|------|----------|

### 4. 发展趋势与展望
（基于现有工作，指出技术趋势、研究空白、未来研究方向）

### 5. 引用格式（GB/T 7714-2015）
> [1] 张三, 李四. 论文题目[J]. 期刊名, 2023, 45(2): 123-130.

## 写作要求
- 严禁虚构不存在的文献！
- 如现有文献信息不足，请基于已知事实合理推断，并注明"根据目前调研"字样
- 每段必须有实质性分析，禁止简单罗列文献标题

## 补充说明
{{additional_context}}""",
     "自主设计，v1：输出符合学术规范的文献综述结构，适用于高校毕业论文"),

    # 分类六：PPT文案撰写 (task_type_id=6)
    ("项目汇报 PPT 讲解稿生成", 6,
     "根据项目信息，生成配套 PPT 每页的讲解稿（Speaker Notes），包含时长建议和关键话术。",
     1,
"""## 任务
你是一名演讲教练和 PPT 制作顾问。请根据以下 PPT 内容，生成每页的讲解稿（Speaker Notes）。

## 项目信息
- 项目名称：{{project_name}}
- 汇报场合：{{presentation_context}}（课程答辩 / 开题汇报 / 中期检查 / 结题汇报 / 竞赛展示）
- 目标受众：{{audience}}（同学 / 老师 / 评委 / 投资人）
- 总时长要求：{{total_duration}} 分钟

## PPT 结构
### Slide 1: 封面
- 标题：{{slide1_title}}
- 副标题：{{slide1_subtitle}}

### Slide 2-N: 各章节内容
{{slide_contents}}

### 最后一页：致谢/Q&A
- 内容：{{final_slide_content}}

## 输出格式
请为每页 PPT 生成独立的讲解稿：

### Slide N: [页面标题]
- **建议时长**：X 分钟 Y 秒
- **核心信息**（一句话）：{{core_message}}
- **讲解稿正文**：
  [开篇话术] {{opening}}
  [主体内容] {{main_content}}
  [过渡话术] {{transition}}
- **关键数据点**：{{data_point_1}}、{{data_point_2}}
- **手势/板书提示**：{{gesture_suggestions}}
- **常见问题预警**（评委可能提问）：{{potential_questions}}

## 演讲技巧建议
- 开场如何吸引注意力（前 30 秒）
- 如何处理技术术语（面向非专业听众时）
- 如何应对忘词/紧张

## 格式要求
- 每个 Slide 的讲解稿不超过 300 字
- 关键数字和术语用 **加粗**
- 过渡话术用 > 引用格式

## 补充说明
{{additional_context}}""",
     "自主设计，v1：适用于高校答辩和项目汇报的 PPT 讲解稿生成"),

    # 分类七：提案修订建议 (task_type_id=7)
    ("文档批注与修订建议生成", 7,
     "对课程报告、项目提案等文档进行内容质量批注，生成具体的修订建议和改进方向。",
     1,
"""## 任务
你是一名严格的学术/课程文档审阅教师。请对以下文档进行详细批注，并给出具体的修订建议。

## 文档信息
- 文档类型：{{doc_type}}（课程报告 / 项目提案 / 毕业论文 / 实验报告）
- 课程/项目名称：{{project_name}}
- 审阅角色：{{reviewer_role}}（任课教师 / 项目导师 / 同行评审）

## 待审阅文档内容
{{document_content}}

## 审阅标准
1）内容完整性：是否涵盖指定要求的所有方面？2）论述深度：论证是否充分？3）逻辑连贯性：章节之间是否衔接自然？4）语言表达：术语是否准确？5）格式规范：标题层级、参考文献格式？6）创新性与价值。

## 输出格式

### 总体评价
- 总体得分：__/100 分
- 优点：{{strengths}}
- 主要不足：{{main_weaknesses}}

### 逐章批注
#### {{chapter_name}}
**评价**：{{chapter_evaluation}} | **得分**：__/100

**批注**：
> 具体问题：[引用原文位置/片段]
> 问题类型：{{issue_type}}
> 建议：{{correction_suggestion}}

### 重点改进建议（前 5 条）
| # | 优先级 | 位置 | 当前问题 | 修改建议 | 预期效果 |
|---|-------|------|---------|---------|---------|

### 修改优先级建议
- 必须修改（影响通过）：{{critical_issues}}
- 建议修改（提升质量）：{{recommended_improvements}}
- 可选优化（锦上添花）：{{optional_improvements}}

## 补充说明
{{additional_context}}""",
     "自主设计，v1：适用于课程报告和项目提案的详细批注与修订建议"),

    ("项目计划修订建议生成", 7,
     "对项目计划书、里程碑和任务分配方案进行评审，给出调整建议和风险提示。",
     1,
"""## 任务
你是一名项目管理专家。请对以下项目计划进行评审，并给出修订建议。

## 项目信息
- 项目名称：{{project_name}}
- 计划周期：{{project_duration}}
- 团队规模：{{team_size}} 人
- 剩余工期：{{remaining_weeks}} 周

## 当前项目状态
{{current_status}}

## 待评审计划内容
### 里程碑计划
{{milestone_plan}}

### 任务分配
{{task_assignments}}

## 评审维度

### 1. 时间可行性
- 各里程碑是否在剩余时间内可完成？
- 是否有过于乐观的时间估算？
- 关键路径是否清晰？

### 2. 任务分配合理性
- 任务量是否在成员能力范围内？
- 是否有依赖关系导致的阻塞风险？

### 3. 风险覆盖
- 已识别风险是否有应对策略（规避/缓解/转移/接受）？
- 是否有未识别的潜在风险？

### 4. 资源匹配
- 人力投入是否与里程碑目标匹配？

## 输出要求

### 综合评估
- 可行性评级：[ ] 完全可行 [ ] 基本可行需微调 [ ] 风险较高需重构
- 核心问题：{{core_issues}}

### 修订建议清单
| # | 优先级 | 当前方案 | 建议调整 | 理由 | 预期效果 |
|---|-------|---------|---------|------|---------|

### 修订后里程碑（草案）
请给出调整后的里程碑时间表草案。

### 风险预警
列出排名前 3 的风险及其缓解建议。

## 补充说明
{{additional_context}}""",
     "自主设计，v1：为项目计划评审和调整提供系统性指导"),

    # 分类八：实验报告总结 (task_type_id=8)
    ("实验报告摘要与总结生成", 8,
     "根据实验目的、方法、数据的描述，生成规范的实验摘要和总结章节。",
     1,
"""## 任务
你是一名实验指导教师。请根据以下实验数据和分析结果，生成规范的实验报告摘要与总结。

## 实验信息
- 实验名称：{{experiment_name}}
- 实验类型：{{experiment_type}}（验证性 / 设计性 / 综合型）
- 项目名称：{{project_name}}

## 实验目的
{{experiment_objectives}}

## 实验环境
- 硬件环境：{{hardware_env}}
- 软件环境：{{software_env}}
- 工具版本：{{tool_versions}}

## 实验步骤摘要
{{experiment_steps}}

## 实验数据与结果
{{experiment_data}}

## 数据分析
{{data_analysis}}

## 输出要求

### 摘要（中英文）
- 中文摘要：200-300 字，包含研究问题、方法、核心发现、主要结论
- 英文摘要：逐句翻译，语法正确，无机翻痕迹

### 总结与反思
#### 实验总结
- 完成情况：{{completion_status}}
- 主要成果：{{main_results}}
- 关键发现：{{key_findings}}（含具体数据）

#### 实验反思
- 成功之处：{{successes}}
- 不足与原因：{{limitations}}
- 改进方向：{{improvement_directions}}

## 格式要求
- 摘要另起一页，中英文各一段，关键词 3-5 个（附英文）
- 总结与反思用 Markdown ## 二级标题

## 补充说明
{{additional_context}}""",
     "自主设计，v1：输出符合高校实验报告规范的摘要与总结"),

    ("项目成果总结报告生成", 8,
     "对已完成的项目进行系统性总结，生成包含成果概述、贡献分析、指标对比的项目总结报告。",
     1,
"""## 任务
你是一名项目总结报告撰写专家。请根据以下项目成果信息，生成一份完整的项目成果总结报告。

## 项目信息
- 项目名称：{{project_name}}
- 项目类型：{{project_type}}（课程设计 / 毕业设计 / 科研项目 / 竞赛作品）
- 团队成员：{{team_members}}
- 完成时间：{{completion_date}}
- 项目评级/分数（如有）：{{project_grade}}

## 项目概述
{{project_overview}}

## 核心成果
{{core_deliverables}}

## 量化指标
| 指标名称 | 目标值 | 实际达成 | 完成率 |
|---------|-------|---------|-------|

## 技术实现
{{technical_implementation}}

## 与需求对比
{{requirements_alignment}}

## 输出要求
报告须包含以下章节：

### 1. 项目概述（背景、目标、范围，1-2 段）

### 2. 成果总览
- 核心交付物清单
- 创新点/亮点（3-5 条，含具体数据或效果）
- 与同类工作的对比（如有）

### 3. 技术实现总结
- 技术架构图（文字描述，Mermaid 语法）
- 关键技术方案及选型理由
- 核心算法或模块说明

### 4. 质量指标达成
- 功能覆盖率：X/Y（百分比）
- 测试覆盖率（如有）：XX%

### 5. 团队贡献分析
| 成员 | 主要贡献 | 工作量占比 |
|------|---------|----------|

### 6. 经验与反思
- 成功经验：{{success_factors}}
- 不足与教训：{{lessons_learned}}
- 后续改进方向：{{future_improvements}}

### 7. 附录（如有）
- 代码仓库地址
- 演示视频链接
- 参考文献

## 格式要求
- Markdown 格式，约 3000-6000 字
- 图表使用 Mermaid 语法（流程图、架构图）
- 代码使用 ``` 标记

## 补充说明
{{additional_context}}""",
     "自主设计，v1：用于高校项目结项时的系统性成果总结报告生成"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Execution
# ─────────────────────────────────────────────────────────────────────────────
def to_utf8(text):
    """Ensure output is valid UTF-8 bytes."""
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    return text

inserted = 0
errors = []

for row in TEMPLATES:
    (template_name, task_type_id, description, version_no, prompt_content, change_note) = row
    try:
        cursor.execute(
            """INSERT INTO prompt_templates
               (template_name, task_type_id, description, is_active, is_deleted, created_at, created_by)
               VALUES (%s, %s, %s, 1, 0, NOW(), 1)""",
            (template_name, task_type_id, description)
        )
        template_id = cursor.lastrowid

        cursor.execute(
            """INSERT INTO prompt_versions
               (template_id, version_no, prompt_content, change_note, is_deleted, created_at, created_by)
               VALUES (%s, %s, %s, %s, 0, NOW(), 1)""",
            (template_id, version_no, prompt_content, change_note)
        )
        version_id = cursor.lastrowid

        cursor.execute(
            "UPDATE prompt_templates SET current_version_id = %s WHERE template_id = %s",
            (version_id, template_id)
        )

        conn.commit()
        inserted += 1
        sys.stdout.buffer.write(f"[OK] {inserted:2d} - {template_name}\n".encode("utf-8"))

    except Exception as e:
        conn.rollback()
        errors.append((template_name, str(e)))
        sys.stdout.buffer.write(f"[ERR] {template_name}: {e}\n".encode("utf-8"))

sys.stdout.buffer.write(f"\n{'='*50}\n".encode("utf-8"))
sys.stdout.buffer.write(f"Inserted : {inserted}/{len(TEMPLATES)}\n".encode("utf-8"))
if errors:
    sys.stdout.buffer.write(f"Errors  : {len(errors)}\n".encode("utf-8"))
    for name, err in errors:
        sys.stdout.buffer.write(f"  - {name}: {err}\n".encode("utf-8"))
else:
    sys.stdout.buffer.write("All templates imported successfully!\n".encode("utf-8"))

cursor.close()
conn.close()
