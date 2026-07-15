-- ============================================================
-- 04_insert_initial_data.sql
-- EduAgent Studio - 初始化数据脚本
-- 包括角色、权限、用户、任务类型、问题标签、模型供应商、模型
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 1. 插入角色数据（4个固定角色）
-- ============================================================

INSERT INTO `roles` (`role_name`, `role_code`, `description`, `status`, `created_by`)
VALUES
    ('学生成员', 'student_member', '项目普通成员，可以创建任务、提交输出、查看本项目内容', 'active', NULL),
    ('项目负责人', 'project_leader', '项目负责人，可以审核本项目输出、添加成员、采纳成果', 'active', NULL),
    ('指导教师', 'teacher', '指导教师，可以查看指导项目并添加意见、审核输出、采纳成果', 'active', NULL),
    ('系统管理员', 'admin', '系统管理员，拥有最高权限，可以管理所有用户、角色、模型和日志', 'active', NULL);

-- ============================================================
-- 2. 插入权限数据
-- ============================================================

INSERT INTO `permissions` (`permission_name`, `permission_code`, `module_name`, `description`, `created_by`)
VALUES
    ('创建项目', 'project:create', 'project', '创建新的项目空间', NULL),
    ('查看项目', 'project:view', 'project', '查看项目详情和成员列表', NULL),
    ('编辑项目', 'project:update', 'project', '修改项目信息', NULL),
    ('删除项目', 'project:delete', 'project', '删除项目（软删除）', NULL),
    ('归档项目', 'project:archive', 'project', '将项目状态设为已归档', NULL),
    ('查看所有项目', 'project:view_all', 'project', '查看系统内所有项目（管理员）', NULL),
    ('添加成员', 'member:add', 'member', '向项目中添加成员', NULL),
    ('移除成员', 'member:remove', 'member', '从项目中移除成员', NULL),
    ('查看成员', 'member:view', 'member', '查看项目成员列表', NULL),
    ('创建任务', 'task:create', 'task', '在项目中创建新任务', NULL),
    ('查看任务', 'task:view', 'task', '查看任务详情', NULL),
    ('编辑任务', 'task:update', 'task', '修改任务信息', NULL),
    ('删除任务', 'task:delete', 'task', '删除任务（软删除）', NULL),
    ('认领任务', 'task:assign_self', 'task', '将任务分配给自己', NULL),
    ('创建分支', 'branch:create', 'branch', '为任务创建新分支', NULL),
    ('查看分支', 'branch:view', 'branch', '查看任务分支', NULL),
    ('合并分支', 'branch:merge', 'branch', '合并分支版本', NULL),
    ('关闭分支', 'branch:close', 'branch', '关闭分支', NULL),
    ('查看输出', 'output:view', 'output', '查看输出版本', NULL),
    ('编辑输出', 'output:edit', 'output', '编辑输出内容', NULL),
    ('提交审核', 'output:submit_review', 'output', '提交输出进行审核', NULL),
    ('采用输出', 'output:adopt', 'output', '将输出采纳为成果', NULL),
    ('删除输出', 'output:delete', 'output', '删除输出版本（软删除）', NULL),
    ('审核输出', 'output:review', 'output', '对输出进行评分和审核', NULL),
    ('查看审核', 'review:view', 'review', '查看审核记录', NULL),
    ('管理模型', 'model:manage', 'model', '添加、编辑、禁用AI模型', NULL),
    ('调用模型', 'model:invoke', 'model', '调用AI模型生成内容', NULL),
    ('查看调用日志', 'model:view_logs', 'model', '查看AI调用记录', NULL),
    ('管理模板', 'template:manage', 'template', '管理提示词模板', NULL),
    ('使用模板', 'template:use', 'template', '使用提示词模板', NULL),
    ('查看成果库', 'artifact:view', 'artifact', '查看项目成果库', NULL),
    ('管理成果', 'artifact:manage', 'artifact', '管理成果（删除、修改元数据）', NULL),
    ('管理用户', 'user:manage', 'user', '创建、编辑、禁用用户账号', NULL),
    ('分配角色', 'user:assign_role', 'user', '为用户分配角色', NULL),
    ('查看用户', 'user:view', 'user', '查看用户列表', NULL),
    ('查看操作日志', 'log:view_operation', 'log', '查看操作日志', NULL),
    ('查看登录日志', 'log:view_login', 'log', '查看登录日志', NULL),
    ('查看成本日志', 'log:view_cost', 'log', '查看成本记录', NULL),
    ('添加批注', 'comment:add', 'comment', '对输出添加批注', NULL),
    ('查看批注', 'comment:view', 'comment', '查看输出批注', NULL),
    ('处理批注', 'comment:resolve', 'comment', '处理/关闭批注', NULL);

-- ============================================================
-- 3. 插入角色权限关联数据
-- ============================================================

-- 学生成员权限
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.role_id, p.permission_id
FROM `roles` r
CROSS JOIN `permissions` p
WHERE r.role_code = 'student_member'
AND p.permission_code IN (
    'project:view', 'project:create',
    'member:view',
    'task:create', 'task:view', 'task:update', 'task:assign_self',
    'branch:create', 'branch:view',
    'output:view', 'output:edit', 'output:submit_review',
    'template:use',
    'artifact:view',
    'user:view',
    'comment:add', 'comment:view'
);

-- 项目负责人权限
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.role_id, p.permission_id
FROM `roles` r
CROSS JOIN `permissions` p
WHERE r.role_code = 'project_leader'
AND p.permission_code IN (
    'project:view', 'project:update', 'project:archive',
    'member:add', 'member:remove', 'member:view',
    'task:create', 'task:view', 'task:update', 'task:delete',
    'branch:create', 'branch:view', 'branch:merge', 'branch:close',
    'output:view', 'output:edit', 'output:submit_review', 'output:adopt', 'output:delete',
    'output:review', 'review:view',
    'model:invoke',
    'template:use',
    'artifact:view', 'artifact:manage',
    'user:view',
    'log:view_operation',
    'comment:add', 'comment:view', 'comment:resolve'
);

-- 指导教师权限
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.role_id, p.permission_id
FROM `roles` r
CROSS JOIN `permissions` p
WHERE r.role_code = 'teacher'
AND p.permission_code IN (
    'project:view_all', 'project:view', 'project:update',
    'member:view',
    'task:view', 'task:update',
    'branch:view',
    'output:view', 'output:edit', 'output:submit_review', 'output:adopt',
    'output:review', 'review:view',
    'model:invoke', 'model:view_logs',
    'template:use', 'template:manage',
    'artifact:view', 'artifact:manage',
    'user:view',
    'log:view_operation', 'log:view_login', 'log:view_cost',
    'comment:add', 'comment:view', 'comment:resolve'
);

-- 管理员权限（全部权限）
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.role_id, p.permission_id
FROM `roles` r
CROSS JOIN `permissions` p
WHERE r.role_code = 'admin';

-- ============================================================
-- 4. 插入管理员用户
-- 演示密码: Pass@1234
-- ============================================================

INSERT INTO `users` (
    `username`, `password_hash`, `real_name`, `student_no`,
    `email`, `phone`, `status`, `last_login_at`, `created_by`
) VALUES (
    'admin',
    '$2b$12$Qcnez8qsfbryeJTPA/STAuHy64Rwz2IZOMXjYR4C5VgxkkvtBx4/y',
    '系统管理员',
    NULL,
    'admin@example.com',
    '13800000000',
    'active',
    NULL,
    NULL
);

-- ============================================================
-- 4b. 插入教师用户
-- 演示密码: Pass@1234
-- ============================================================
INSERT INTO `users` (
    `username`, `password_hash`, `real_name`, `student_no`,
    `email`, `phone`, `status`, `last_login_at`, `created_by`
) VALUES (
    'teacher_li',
    '$2b$12$Qcnez8qsfbryeJTPA/STAuHy64Rwz2IZOMXjYR4C5VgxkkvtBx4/y',
    '李建国',
    NULL,
    'li.jianguo@eduagent.local',
    '13800000001',
    'active',
    NULL,
    NULL
);

-- ============================================================
-- 4c. 插入学生用户
-- 演示密码: Pass@1234
-- ============================================================
INSERT INTO `users` (
    `username`, `password_hash`, `real_name`, `student_no`,
    `email`, `phone`, `status`, `last_login_at`, `created_by`
) VALUES
    ('student_zhang', '$2b$12$Qcnez8qsfbryeJTPA/STAuHy64Rwz2IZOMXjYR4C5VgxkkvtBx4/y', '张小明', '2024001001', 'zhang.xm@eduagent.local', '13800000201', 'active', NULL, NULL),
    ('student_liu', '$2b$12$Qcnez8qsfbryeJTPA/STAuHy64Rwz2IZOMXjYR4C5VgxkkvtBx4/y', '刘洋', '2024001002', 'liu.yang@eduagent.local', '13800000202', 'active', NULL, NULL),
    ('student_chen', '$2b$12$Qcnez8qsfbryeJTPA/STAuHy64Rwz2IZOMXjYR4C5VgxkkvtBx4/y', '陈雨欣', '2024001003', 'chen.yx@eduagent.local', '13800000203', 'active', NULL, NULL);

-- ============================================================
-- 5. 为管理员分配 admin 角色
-- ============================================================

INSERT INTO `user_roles` (`user_id`, `role_id`, `assigned_by`)
SELECT u.user_id, r.role_id, NULL
FROM `users` u, `roles` r
WHERE u.username = 'admin' AND r.role_code = 'admin';

-- ============================================================
-- 5b. 为教师分配 teacher 角色
-- ============================================================
INSERT INTO `user_roles` (`user_id`, `role_id`, `assigned_by`)
SELECT u.user_id, r.role_id, NULL
FROM `users` u, `roles` r
WHERE u.username = 'teacher_li' AND r.role_code = 'teacher';

-- ============================================================
-- 5c. 为学生分配 student_member 角色
-- ============================================================
INSERT INTO `user_roles` (`user_id`, `role_id`, `assigned_by`)
SELECT u.user_id, r.role_id, NULL
FROM `users` u, `roles` r
WHERE u.username IN ('student_zhang', 'student_liu', 'student_chen') AND r.role_code = 'student_member';

-- ============================================================
-- 6. 插入任务类型数据（9个常用任务类型）
-- ============================================================

INSERT INTO `task_types` (`type_name`, `type_code`, `description`, `status`, `created_by`)
VALUES
    ('需求分析生成', 'requirement_analysis', '根据项目背景和目标，生成需求分析文档初稿', 'active', NULL),
    ('数据库表设计建议', 'db_schema_design', '根据业务描述，生成数据库表结构设计建议', 'active', NULL),
    ('SQL代码解释', 'sql_explanation', '对给定的SQL语句进行详细解释', 'active', NULL),
    ('论文摘要润色', 'paper_abstract_polish', '对论文摘要进行语言润色', 'active', NULL),
    ('文献内容总结', 'literature_summary', '对文献内容进行摘要和关键点提取', 'active', NULL),
    ('PPT文案优化', 'ppt_copywriting', '对PPT演示文案的文字内容进行优化', 'active', NULL),
    ('项目申报书修改', 'proposal_revision', '对项目申报书内容进行修改完善', 'active', NULL),
    ('实验报告总结', 'experiment_summary', '对实验数据进行整理，生成规范的实验报告总结', 'active', NULL),
    ('代码注释生成', 'code_annotation', '为代码文件或函数生成规范的中文注释说明', 'active', NULL);

-- ============================================================
-- 7. 插入问题标签数据（10个常见问题标签）
-- severity 枚举值：low/medium/high
-- ============================================================

INSERT INTO `issue_tags` (`tag_name`, `tag_code`, `description`, `severity`, `created_by`)
VALUES
    ('内容空泛', 'content_vague', '输出内容过于笼统，缺乏具体细节和可操作性', 'medium', NULL),
    ('事实错误', 'factual_error', '输出内容存在事实性错误或与已知事实不符', 'high', NULL),
    ('逻辑混乱', 'logic_confusion', '论述逻辑不清晰，前后矛盾或推理过程有问题', 'medium', NULL),
    ('格式不规范', 'format_issues', '输出格式不符合要求', 'low', NULL),
    ('任务偏离', 'off_topic', '输出内容偏离了原始任务要求', 'medium', NULL),
    ('重复啰嗦', 'redundant', '内容重复、表述冗余', 'low', NULL),
    ('缺少依据', 'lack_evidence', '重要结论缺乏数据或文献支撑', 'medium', NULL),
    ('风险内容', 'risk_content', '输出内容涉及政治敏感、色情暴力、隐私泄露等风险', 'high', NULL),
    ('SQL错误', 'sql_error', 'SQL语句存在语法错误或逻辑错误', 'high', NULL),
    ('代码不可运行', 'code_unrunnable', '代码存在语法错误、依赖缺失或逻辑问题', 'high', NULL);

-- ============================================================
-- 8. 插入模型供应商数据
-- ============================================================

INSERT INTO `model_providers` (`provider_name`, `provider_code`, `base_url`, `website`, `description`, `status`, `created_by`)
VALUES
    ('Mock Provider', 'mock', NULL, NULL, 'Mock 模型供应商，用于课程设计和功能测试', 'active', NULL),
    ('OpenAI', 'openai', 'https://api.openai.com/v1', 'https://openai.com', 'OpenAI GPT 系列模型供应商', 'active', NULL),
    ('DeepSeek', 'deepseek', 'https://api.deepseek.com/v1', 'https://deepseek.com', 'DeepSeek 系列模型供应商', 'active', NULL);

-- ============================================================
-- 9. 插入AI模型数据
-- 3个 Mock 模型（不产生真实费用）+ 5个真实模型示例
-- ============================================================

INSERT INTO `ai_models` (
    `provider_id`, `model_name`, `display_name`, `capability_tags`,
    `max_context`, `input_price`, `output_price`, `price_unit`, `status`, `created_by`
) VALUES
    -- Mock 模型（课程设计用，定价为 0）
    (1, 'mock-writer', 'Mock-Writer', '文本生成,写作辅助,润色',
     4096, 0.000000, 0.000000, '1K_TOKENS', 'active', NULL),
    (1, 'mock-code', 'Mock-Code', '代码生成,SQL,代码解释',
     4096, 0.000000, 0.000000, '1K_TOKENS', 'active', NULL),
    (1, 'mock-reviewer', 'Mock-Reviewer', '审核,评分,问题标注',
     4096, 0.000000, 0.000000, '1K_TOKENS', 'active', NULL),
    -- OpenAI 模型
    (2, 'gpt-4o', 'GPT-4o', '文本生成,代码,多模态',
     128000, 0.002500, 0.010000, '1K_TOKENS', 'active', NULL),
    (2, 'gpt-4o-mini', 'GPT-4o-mini', '文本生成,代码,轻量',
     128000, 0.000150, 0.000600, '1K_TOKENS', 'active', NULL),
    (2, 'gpt-3.5-turbo', 'GPT-3.5-Turbo', '文本生成,快速响应',
     16385, 0.000500, 0.001500, '1K_TOKENS', 'disabled', NULL),
    -- DeepSeek 模型
    (3, 'deepseek-chat', 'DeepSeek-Chat', '文本生成,对话,分析',
     64000, 0.000100, 0.000300, '1K_TOKENS', 'active', NULL),
    (3, 'deepseek-coder', 'DeepSeek-Coder', '代码生成,代码补全,代码解释',
     64000, 0.000140, 0.000420, '1K_TOKENS', 'active', NULL);

-- ============================================================
-- 10. 插入 API 配置数据（加密字段使用占位值）
-- ============================================================

INSERT INTO `api_configs` (
    `provider_id`, `config_name`, `encrypted_api_key`, `key_iv`, `key_tag`,
    `key_version`, `key_mask`, `quota_limit`, `used_quota`, `status`, `created_by`
) VALUES
    (1, 'Mock 默认配置', 'MOCK_KEY_PLACEHOLDER', 'MOCK_IV_PLACEHOLDER', 'MOCK_TAG_PLACEHOLDER',
     1, 'mock-****mock', 999999.00, 0.00, 'active', NULL),
    (2, 'OpenAI API 配置（测试）', 'OPENAI_KEY_PLACEHOLDER', 'OPENAI_IV_PLACEHOLDER', 'OPENAI_TAG_PLACEHOLDER',
     1, 'sk-****test', 100.00, 0.00, 'active', NULL),
    (3, 'DeepSeek API 配置（测试）', 'DEEPSEEK_KEY_PLACEHOLDER', 'DEEPSEEK_IV_PLACEHOLDER', 'DEEPSEEK_TAG_PLACEHOLDER',
     1, 'sk-****dsk', 100.00, 0.00, 'active', NULL);
