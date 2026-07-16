-- Align prompt governance with the EduAgent education workflow.
USE `ai_collab_audit_system`;

UPDATE prompt_templates
SET is_active = 0,
    is_deleted = 1,
    deleted_at = COALESCE(deleted_at, NOW()),
    updated_at = NOW()
WHERE is_deleted = 0
  AND template_name IN (
    '项目需求分析生成',
    '敏捷用户故事生成',
    '毕业设计开题报告生成',
    '需求变更影响分析',
    '项目组会议纪要生成',
    'AI 提示词质量评审与优化',
    'AI 辅助课程报告生成',
    '数据库概念设计生成',
    'MySQL DDL 建表语句生成',
    '数据库课程设计报告生成',
    'AI 生成代码质量审核',
    'SQL 查询质量审核',
    'Python REST API CRUD 生成',
    '复杂 SQL 查询生成',
    'RESTful API 文档生成',
    '代码审查意见生成',
    '函数级代码注释生成',
    'Python 单元测试用例生成',
    '文献综述章节生成',
    '项目汇报 PPT 讲解稿生成',
    '文档批注与修订建议生成',
    '项目计划修订建议生成',
    '实验报告摘要与总结生成',
    '项目成果总结报告生成'
  );

UPDATE task_types
SET status = 'disabled',
    updated_at = NOW()
WHERE type_code IN (
  'lecture_generation',
  'db_schema_design',
  'sql_explanation',
  'paper_abstract_polish',
  'literature_summary',
  'ppt_copywriting',
  'proposal_revision',
  'experiment_summary',
  'code_annotation',
  'ppt_generation',
  'quiz_generation',
  'case_generation',
  'review_plan_generation',
  'test_generation'
);

INSERT INTO task_types (type_name, type_code, description, status, is_deleted)
VALUES
  ('课程讲义生成', 'lecture', '基于课程知识点、学生画像和教材证据生成个性化讲义', 'active', 0),
  ('练习题生成', 'quiz', '按掌握度和难度生成分层练习、答案与解析', 'active', 0),
  ('案例分析', 'case', '生成与知识点对应的真实情境案例和引导问题', 'active', 0),
  ('内容审核', 'review', '辅助教师审核资源质量、证据、风险和可用性', 'active', 0),
  ('知识总结', 'summary', '根据学习记录和薄弱点生成个性化总结', 'active', 0),
  ('学习画像诊断', 'profile_diagnosis', '从学习行为、测评和反馈中诊断能力与薄弱点', 'active', 0),
  ('循证学习答疑', 'tutor_answer', '结合课程上下文、学生画像和知识库证据回答问题', 'active', 0),
  ('事实与证据校验', 'evidence_check', '检查生成内容的事实一致性、引用完整性和幻觉风险', 'active', 0)
ON DUPLICATE KEY UPDATE
  type_name = VALUES(type_name),
  description = VALUES(description),
  status = 'active',
  is_deleted = 0,
  deleted_at = NULL,
  updated_at = NOW();

CREATE TEMPORARY TABLE education_prompt_seed (
  type_code VARCHAR(50) NOT NULL,
  template_name VARCHAR(200) NOT NULL,
  description VARCHAR(500) NOT NULL,
  prompt_content TEXT NOT NULL
);

INSERT INTO education_prompt_seed (type_code, template_name, description, prompt_content)
VALUES
  ('lecture', '个性化课程讲义生成', '依据课程知识点、学生画像和教材证据生成可学习、可追溯的讲义。',
   '你是课程讲义生成智能体。请根据课程 {{course_name}}、知识点 {{knowledge_point}}、学习目标 {{learning_objective}}、学生画像 {{student_profile}} 和教材证据 {{evidence}} 生成讲义。内容必须包含学习目标、先备知识、核心概念、分步讲解、例题、易错点、自检问题和证据引用。不得编造证据中不存在的事实，信息不足时明确说明。'),
  ('quiz', '分层练习与答案生成', '根据掌握度生成不同难度的练习题、答案和诊断标签。',
   '你是分层练习生成智能体。围绕 {{knowledge_point}}，结合学生掌握度 {{mastery_level}}、目标难度 {{difficulty}} 和教材证据 {{evidence}} 生成练习。每题必须提供题型、题干、答案、解析、知识点标签、难度和常见错误。题目应由易到难，答案不得依赖题干之外的隐含条件。'),
  ('case', '真实情境案例资源生成', '把课程知识点转化为可讨论、可实践的真实情境案例。',
   '你是教学案例生成智能体。请围绕课程 {{course_name}} 的知识点 {{knowledge_point}}，面向 {{student_profile}} 生成真实情境案例。输出背景、任务、约束、数据或素材、分析步骤、引导问题、参考方案、评价标准和教材证据。案例必须可执行，避免虚构机构、政策或统计结论。'),
  ('review', '教师内容审核清单', '从正确性、证据、安全性和教学可用性辅助教师审核资源。',
   '你是教师审核辅助智能体。请审核资源 {{resource_content}}，并结合课程目标 {{learning_objective}} 与证据 {{evidence}} 给出结论。逐项评估事实正确性、知识覆盖、难度适配、逻辑结构、引用完整性、内容安全和教学可用性。输出通过、退回修改或拒绝，并列出可定位的问题、风险等级和具体修改建议。'),
  ('summary', '个性化学习总结生成', '根据学习记录和测评结果总结进展并安排下一步学习。',
   '你是学习总结智能体。请根据学生画像 {{student_profile}}、学习记录 {{learning_history}}、测评结果 {{assessment_results}} 和课程知识点 {{knowledge_points}} 生成总结。输出已掌握内容、进步证据、薄弱点、错误模式、优先级、下一步任务和可量化目标。结论必须能追溯到输入数据。'),
  ('profile_diagnosis', '学习画像诊断', '从多源学习数据提取稳定特征、薄弱点和学习偏好。',
   '你是学习画像诊断智能体。请分析学生基本信息 {{student_info}}、学习行为 {{learning_events}}、测评记录 {{assessment_results}} 和主观反馈 {{feedback}}。输出当前水平、已掌握能力、薄弱知识点、错误模式、资源偏好、可用学习时间、诊断置信度和证据。不得根据姓名、性别或无关属性推断能力。'),
  ('tutor_answer', '循证学习答疑', '结合画像、学习路径和知识库证据生成分层答疑。',
   '你是循证学习辅导智能体。请回答问题 {{question}}，并结合课程 {{course_name}}、学生画像 {{student_profile}}、学习路径 {{learning_path}} 和知识库证据 {{evidence}}。先判断意图，再给出适合当前水平的解释、关键步骤、例子和自检问题。引用教材时标明来源，证据不足时说明边界并请求补充信息。'),
  ('evidence_check', '事实与证据一致性校验', '识别无依据结论、引用错配和潜在幻觉。',
   '你是事实与证据校验智能体。请对生成内容 {{generated_content}} 和证据集合 {{evidence}} 逐条核验。输出事实声明、对应证据、支持程度、引用是否准确、缺失证据、冲突信息和风险等级。将无法验证的内容标记为待确认，不得用常识猜测替代课程证据。');

INSERT INTO prompt_templates (
  template_name,
  task_type_id,
  description,
  current_version_id,
  is_active,
  is_deleted,
  created_at,
  created_by
)
SELECT
  seed.template_name,
  tt.task_type_id,
  seed.description,
  NULL,
  1,
  0,
  NOW(),
  (SELECT user_id FROM users WHERE username = 'admin' AND is_deleted = 0 LIMIT 1)
FROM education_prompt_seed seed
INNER JOIN task_types tt
  ON tt.type_code = seed.type_code
 AND tt.is_deleted = 0
WHERE NOT EXISTS (
  SELECT 1
  FROM prompt_templates existing
  WHERE existing.template_name = seed.template_name
    AND existing.is_deleted = 0
);

INSERT INTO prompt_versions (
  template_id,
  version_no,
  prompt_content,
  change_note,
  is_deleted,
  created_at,
  created_by
)
SELECT
  pt.template_id,
  1,
  seed.prompt_content,
  '教育多智能体正式模板',
  0,
  NOW(),
  (SELECT user_id FROM users WHERE username = 'admin' AND is_deleted = 0 LIMIT 1)
FROM education_prompt_seed seed
INNER JOIN prompt_templates pt
  ON pt.template_name = seed.template_name
 AND pt.is_deleted = 0
WHERE NOT EXISTS (
  SELECT 1
  FROM prompt_versions existing
  WHERE existing.template_id = pt.template_id
    AND existing.version_no = 1
    AND existing.is_deleted = 0
);

UPDATE prompt_templates pt
INNER JOIN prompt_versions pv
  ON pv.template_id = pt.template_id
 AND pv.version_no = 1
 AND pv.is_deleted = 0
INNER JOIN education_prompt_seed seed
  ON seed.template_name = pt.template_name
SET pt.current_version_id = pv.prompt_version_id,
    pt.is_active = 1,
    pt.updated_at = NOW()
WHERE pt.is_deleted = 0;

UPDATE task_types tt
INNER JOIN prompt_templates pt
  ON pt.task_type_id = tt.task_type_id
 AND pt.is_deleted = 0
 AND pt.is_active = 1
INNER JOIN education_prompt_seed seed
  ON seed.template_name = pt.template_name
SET tt.default_template_id = pt.template_id,
    tt.updated_at = NOW();

DROP TEMPORARY TABLE education_prompt_seed;
