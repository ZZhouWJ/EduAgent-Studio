-- ============================================================
-- 07_test_queries.sql
-- AI-Collab-Audit-System - 测试查询脚本
--
-- 枚举值（严格遵守 Schema）：
--   task_outputs.status:
--     draft/generated/submitted/approved/rejected/revision_required/adopted/conflict_pending
--   project_members.project_role: member/leader/reviewer/teacher
--   output_comments.status: open/resolved/closed
--   issue_tags.severity: low/medium/high
--   merge_records.merge_strategy:
--     adopt_source/adopt_target/manual_merge/adopt_separately
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 测试1：查询用户和角色
-- ============================================================

SELECT user_id, username, real_name, email, status, created_at
FROM users WHERE is_deleted = 0 ORDER BY created_at;

SELECT role_id, role_name, role_code, description, status
FROM roles WHERE is_deleted = 0 ORDER BY role_id;

SELECT ur.user_role_id, u.username, u.real_name, r.role_name, r.role_code, ur.assigned_at
FROM user_roles ur
INNER JOIN users u ON ur.user_id = u.user_id AND u.is_deleted = 0
INNER JOIN roles r ON ur.role_id = r.role_id AND r.is_deleted = 0
WHERE ur.is_deleted = 0
ORDER BY ur.assigned_at DESC;

SELECT user_id, username, real_name, user_status, roles, permission_count, permissions
FROM v_user_permissions
WHERE user_status = 'active';

-- ============================================================
-- 测试2：查询项目任务统计视图
-- ============================================================

SELECT
    project_id, project_name, project_type, owner_name, project_status,
    total_members, total_tasks,
    task_draft, task_running, task_generated,
    task_submitted, task_approved, task_rejected,
    task_revision_required, task_adopted, task_archived, task_conflict_pending,
    total_outputs, pending_reviews
FROM v_project_task_statistics
ORDER BY project_created_at DESC;

-- ============================================================
-- 测试3：查询模型调用统计视图
-- ============================================================

SELECT
    model_id, model_name, display_name, provider_name, model_status,
    total_invocations, success_count, failed_count, success_rate,
    total_input_tokens, total_output_tokens, total_tokens,
    total_cost, avg_latency_ms
FROM v_model_invocation_statistics
ORDER BY total_invocations DESC;

-- ============================================================
-- 测试4：查询待审核输出
-- ============================================================

SELECT
    request_id, project_name, task_title, output_title,
    submitter_name, submit_note, submit_time
FROM v_pending_reviews
ORDER BY submit_time ASC;

-- ============================================================
-- 测试5：查询项目成果库
-- ============================================================

SELECT
    adopted_id, project_name, task_title, artifact_title,
    artifact_type, release_version, adopted_by_name, adopted_at
FROM v_artifacts
ORDER BY adopted_at DESC;

-- ============================================================
-- 测试6：查询输出版本时间线（WITH RECURSIVE）
-- 递归查询某个输出的完整版本链路
-- ============================================================

SET @target_output_id = 1;

WITH RECURSIVE output_lineage AS (
    SELECT
        o.output_id, o.task_id, o.parent_output_id, o.version_no,
        o.output_title, o.source_type, o.lock_version,
        o.edit_summary, o.last_modified_at,
        u.real_name AS last_modified_by_name,
        o.created_at, cu.real_name AS created_by_name,
        1 AS depth,
        CAST(o.output_id AS CHAR(1000)) AS path
    FROM task_outputs o
    LEFT JOIN users u ON o.last_modified_by = u.user_id AND u.is_deleted = 0
    LEFT JOIN users cu ON o.created_by = cu.user_id AND cu.is_deleted = 0
    WHERE o.output_id = @target_output_id AND o.is_deleted = 0
    UNION ALL
    SELECT
        o.output_id, o.task_id, o.parent_output_id, o.version_no,
        o.output_title, o.source_type, o.lock_version,
        o.edit_summary, o.last_modified_at,
        u.real_name AS last_modified_by_name,
        o.created_at, cu.real_name AS created_by_name,
        ol.depth + 1 AS depth,
        CONCAT(ol.path, '->', o.output_id) AS path
    FROM output_lineage ol
    INNER JOIN task_outputs o
        ON ol.parent_output_id = o.output_id AND o.is_deleted = 0
    LEFT JOIN users u ON o.last_modified_by = u.user_id AND u.is_deleted = 0
    LEFT JOIN users cu ON o.created_by = cu.user_id AND cu.is_deleted = 0
    WHERE ol.depth < 50
)
SELECT
    depth, output_id, task_id, parent_output_id,
    version_no, output_title, source_type, lock_version,
    edit_summary, last_modified_at, last_modified_by_name,
    created_at, created_by_name, path
FROM output_lineage
ORDER BY depth ASC;

-- ============================================================
-- 测试7：验证初始化数据中的状态值
-- ============================================================

SELECT task_type_id, type_code, type_name FROM task_types WHERE is_deleted = 0 ORDER BY task_type_id;

-- issue_tags.severity 应为 low/medium/high
SELECT tag_id, tag_name, tag_code, description, severity
FROM issue_tags WHERE is_deleted = 0 ORDER BY severity, tag_id;

-- ai_models 应包含 3 个 Mock 模型
SELECT model_id, model_name, display_name, input_price, output_price, price_unit
FROM ai_models WHERE is_deleted = 0 ORDER BY model_id;

-- ============================================================
-- 测试8：测试触发器（审核通过自动写日志）
-- ============================================================

-- 8.1 插入测试项目
INSERT INTO projects (project_name, project_type, description, owner_id, status, created_by)
VALUES ('触发器测试项目', 'course_project', '用于测试触发器', 1, 'active', 1);
SET @tp = LAST_INSERT_ID();

-- 8.2 插入测试任务（确保 task_types 有数据）
INSERT INTO project_tasks (project_id, task_type_id, title, description, creator_id, assignee_id, status, priority, created_by)
SELECT @tp, task_type_id, '触发器测试任务', '测试触发器', 1, 1, 'draft', 'normal', 1
FROM task_types WHERE is_deleted = 0 LIMIT 1;
SET @tt = LAST_INSERT_ID();

-- 8.3 插入测试分支（列顺序：project_id, task_id, branch_name, base_output_id, status, created_by）
INSERT INTO task_branches (project_id, task_id, branch_name, base_output_id, status, created_by)
VALUES (@tp, @tt, 'feature-test-trigger', NULL, 'active', 1);
SET @tb = LAST_INSERT_ID();

-- 8.4 插入测试输出（task_outputs.status 初始为 draft）
INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@tt, @tb, 1, '触发器测试输出', '# 测试\n\n测试内容。', 'ai_generated', 'draft', 1);
SET @to = LAST_INSERT_ID();

-- 8.5 插入审核请求（request_status = pending）
INSERT INTO review_requests (output_id, task_id, project_id, submitter_id, reviewer_id, request_status, submit_note, created_by)
VALUES (@to, @tt, @tp, 1, 1, 'pending', '提交触发器测试', 1);
SET @tr = LAST_INSERT_ID();

-- 8.6 插入审核记录（review_status = approved）
-- 触发器 trg_output_review_approved 应自动在 operation_logs 写入记录
INSERT INTO output_reviews (
    request_id, output_id, reviewer_id,
    accuracy_score, completeness_score, logic_score, format_score, usability_score, risk_score,
    review_status, review_comment, reviewed_at, created_by
) VALUES (
    @tr, @to, 1,
    9.0, 8.5, 9.0, 8.0, 9.0, 1.0,
    'approved',
    '整体质量良好，触发器测试通过。',
    NOW(), 1
);

-- 8.7 验证触发器日志已写入
SELECT
    log_id, user_id, project_id, task_id,
    target_type, target_id, action_type, action_desc,
    LEFT(new_value, 200) AS new_value_preview, created_at
FROM operation_logs
WHERE action_type = 'review_approved'
ORDER BY created_at DESC LIMIT 5;

-- ============================================================
-- 测试9：测试 sp_archive_project 存储过程
-- ============================================================

-- 9.1 创建待归档测试项目
INSERT INTO projects (project_name, project_type, description, owner_id, status, created_by)
VALUES ('待归档测试项目', 'research_project', '用于测试归档存储过程', 1, 'active', 1);
SET @ap = LAST_INSERT_ID();

INSERT INTO project_tasks (project_id, task_type_id, title, description, creator_id, assignee_id, status, priority, created_by)
SELECT @ap, task_type_id, '归档测试任务1', '测试归档', 1, 1, 'generated', 'high', 1
FROM task_types WHERE is_deleted = 0 LIMIT 1;
SET @at1 = LAST_INSERT_ID();

INSERT INTO project_tasks (project_id, task_type_id, title, description, creator_id, assignee_id, status, priority, created_by)
SELECT @ap, task_type_id, '归档测试任务2', '测试归档', 1, 1, 'running', 'normal', 1
FROM task_types WHERE is_deleted = 0 LIMIT 1;
SET @at2 = LAST_INSERT_ID();

-- 9.1 创建待归档测试项目
INSERT INTO task_branches (project_id, task_id, branch_name, base_output_id, status, created_by)
VALUES
    (@ap, @at1, 'feature-archive-1', NULL, 'active', 1),
    (@ap, @at2, 'feature-archive-2', NULL, 'active', 1);

-- 9.2 调用 sp_archive_project
SET @archive_code = 0;
SET @archive_msg = '';
CALL sp_archive_project(@ap, 1, @archive_code, @archive_msg);
SELECT @archive_code AS result_code, @archive_msg AS result_message;

-- 9.3 验证项目状态
SELECT project_id, project_name, status FROM projects WHERE project_id = @ap;

-- 9.4 验证任务状态（应为 archived）
SELECT task_id, title, status FROM project_tasks WHERE project_id = @ap;

-- 9.5 验证分支状态（应为 closed）
SELECT branch_id, branch_name, status FROM task_branches WHERE project_id = @ap;

-- 9.6 验证归档日志
SELECT
    log_id, action_type, action_desc,
    JSON_EXTRACT(new_value, '$.status') AS new_status,
    JSON_EXTRACT(new_value, '$.archived_tasks') AS archived_tasks,
    JSON_EXTRACT(new_value, '$.archived_branches') AS archived_branches
FROM operation_logs
WHERE action_type = 'project_archive' AND project_id = @ap;

-- ============================================================
-- 测试10：测试 sp_create_project_with_owner
-- ============================================================

SET @new_proj_id = 0;
SET @create_code = 0;
SET @create_msg = '';

CALL sp_create_project_with_owner(
    'SP创建测试项目', 'course_project',
    '测试存储过程创建项目', 1, 1,
    @create_code, @create_msg, @new_proj_id
);

SELECT @create_code AS result_code, @create_msg AS result_message, @new_proj_id AS new_project_id;

-- 验证项目成员中创建人被自动添加为 leader
SELECT pm.member_id, pm.project_id, pm.user_id, u.real_name, pm.project_role, pm.status
FROM project_members pm
INNER JOIN users u ON pm.user_id = u.user_id
WHERE pm.project_id = @new_proj_id AND pm.is_deleted = 0;

-- ============================================================
-- 测试11：验证 task_outputs.status 枚举
-- 确认所有状态值都能正常写入
-- ============================================================

-- 测试各状态值是否可写入
INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试draft', '内容draft', 'ai_generated', 'draft', 1);

INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试generated', '内容generated', 'ai_generated', 'generated', 1);

INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试submitted', '内容submitted', 'manual_edit', 'submitted', 1);

INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试approved', '内容approved', 'hybrid', 'approved', 1);

INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试rejected', '内容rejected', 'manual_edit', 'rejected', 1);

INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试revision_required', '内容revision_required', 'manual_edit', 'revision_required', 1);

INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试adopted', '内容adopted', 'hybrid', 'adopted', 1);

INSERT INTO task_outputs (task_id, branch_id, version_no, output_title, content, source_type, status, created_by)
VALUES (@at1, NULL, 1, '测试conflict_pending', '内容conflict_pending', 'manual_merge', 'conflict_pending', 1);

-- 验证所有状态值均已写入
SELECT DISTINCT status, COUNT(*) AS count FROM task_outputs WHERE is_deleted = 0 GROUP BY status;

-- ============================================================
-- 测试12：验证 project_members.project_role 枚举
-- ============================================================

-- 更新触发器测试项目成员的 project_role
UPDATE project_members SET project_role = 'leader' WHERE project_id = @tp AND is_deleted = 0;
UPDATE project_members SET project_role = 'reviewer' WHERE project_id = @tp AND is_deleted = 0;

-- 验证 project_role 枚举值
SELECT DISTINCT project_role, COUNT(*) AS count FROM project_members WHERE is_deleted = 0 GROUP BY project_role;

-- ============================================================
-- 测试13：验证 output_comments.status 枚举
-- ============================================================

INSERT INTO output_comments (output_id, commenter_id, comment_type, comment_text, status, created_by)
VALUES (@to, 1, 'comment', '测试批注-open', 'open', 1);

INSERT INTO output_comments (output_id, commenter_id, comment_type, comment_text, status, created_by)
VALUES (@to, 1, 'suggestion', '测试批注-resolved', 'resolved', 1);

INSERT INTO output_comments (output_id, commenter_id, comment_type, comment_text, status, created_by)
VALUES (@to, 1, 'approval', '测试批注-closed', 'closed', 1);

SELECT DISTINCT status, COUNT(*) AS count FROM output_comments WHERE is_deleted = 0 GROUP BY status;

-- ============================================================
-- 测试14：验证 merge_records.merge_strategy 枚举
-- ============================================================

INSERT INTO merge_records (project_id, task_id, base_output_id, source_output_id, target_output_id, merge_strategy, merge_comment, merged_by)
VALUES
    (@tp, @tt, NULL, NULL, NULL, 'adopt_source', '采用来源版本', 1),
    (@tp, @tt, NULL, NULL, NULL, 'adopt_target', '采用目标版本', 1),
    (@tp, @tt, NULL, NULL, NULL, 'manual_merge', '手动合并', 1),
    (@tp, @tt, NULL, NULL, NULL, 'adopt_separately', '分别采用', 1);

SELECT DISTINCT merge_strategy, COUNT(*) AS count FROM merge_records WHERE is_deleted = 0 GROUP BY merge_strategy;

-- ============================================================
-- 测试15：验证 issue_tags.severity 枚举
-- ============================================================

-- 验证 severity 枚举值（初始化数据中已包含）
SELECT tag_id, tag_name, tag_code, severity FROM issue_tags WHERE is_deleted = 0 ORDER BY severity;

-- ============================================================
-- 测试16：验证表结构和约束
-- ============================================================

-- 16.1 统计表数量（应为 27）
SELECT COUNT(*) AS total_tables
FROM information_schema.tables
WHERE table_schema = 'ai_collab_audit_system' AND table_type = 'BASE TABLE';

-- 16.2 列出所有表
SELECT table_name,
       ROUND(data_length / 1024, 2) AS data_size_kb,
       ROUND(index_length / 1024, 2) AS index_size_kb
FROM information_schema.tables
WHERE table_schema = 'ai_collab_audit_system' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 16.3 统计各表记录数
SELECT 'users' AS tbl, COUNT(*) AS cnt FROM users WHERE is_deleted = 0
UNION ALL SELECT 'roles', COUNT(*) FROM roles WHERE is_deleted = 0
UNION ALL SELECT 'user_roles', COUNT(*) FROM user_roles WHERE is_deleted = 0
UNION ALL SELECT 'permissions', COUNT(*) FROM permissions WHERE is_deleted = 0
UNION ALL SELECT 'role_permissions', COUNT(*) FROM role_permissions WHERE is_deleted = 0
UNION ALL SELECT 'task_types', COUNT(*) FROM task_types WHERE is_deleted = 0
UNION ALL SELECT 'issue_tags', COUNT(*) FROM issue_tags WHERE is_deleted = 0
UNION ALL SELECT 'model_providers', COUNT(*) FROM model_providers WHERE is_deleted = 0
UNION ALL SELECT 'ai_models', COUNT(*) FROM ai_models WHERE is_deleted = 0
UNION ALL SELECT 'api_configs', COUNT(*) FROM api_configs WHERE is_deleted = 0
UNION ALL SELECT 'projects', COUNT(*) FROM projects WHERE is_deleted = 0
UNION ALL SELECT 'project_members', COUNT(*) FROM project_members WHERE is_deleted = 0
UNION ALL SELECT 'project_tasks', COUNT(*) FROM project_tasks WHERE is_deleted = 0
UNION ALL SELECT 'task_branches', COUNT(*) FROM task_branches WHERE is_deleted = 0
UNION ALL SELECT 'task_outputs', COUNT(*) FROM task_outputs WHERE is_deleted = 0
UNION ALL SELECT 'review_requests', COUNT(*) FROM review_requests WHERE is_deleted = 0
UNION ALL SELECT 'output_reviews', COUNT(*) FROM output_reviews WHERE is_deleted = 0
UNION ALL SELECT 'output_comments', COUNT(*) FROM output_comments WHERE is_deleted = 0
UNION ALL SELECT 'merge_records', COUNT(*) FROM merge_records WHERE is_deleted = 0
UNION ALL SELECT 'adopted_outputs', COUNT(*) FROM adopted_outputs WHERE is_deleted = 0
UNION ALL SELECT 'prompt_templates', COUNT(*) FROM prompt_templates WHERE is_deleted = 0
UNION ALL SELECT 'prompt_versions', COUNT(*) FROM prompt_versions WHERE is_deleted = 0
UNION ALL SELECT 'output_issue_relations', COUNT(*) FROM output_issue_relations WHERE is_deleted = 0
UNION ALL SELECT 'ai_invocations', COUNT(*) FROM ai_invocations
UNION ALL SELECT 'cost_records', COUNT(*) FROM cost_records
UNION ALL SELECT 'operation_logs', COUNT(*) FROM operation_logs
UNION ALL SELECT 'login_logs', COUNT(*) FROM login_logs
ORDER BY tbl;

-- 16.4 列出所有视图
SELECT table_name AS view_name
FROM information_schema.views
WHERE table_schema = 'ai_collab_audit_system'
ORDER BY table_name;

-- 16.5 列出所有存储过程
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'ai_collab_audit_system' AND routine_type = 'PROCEDURE'
ORDER BY routine_name;

-- 16.6 列出所有触发器
SELECT trigger_name, event_object_table AS table_name, action_timing AS timing
FROM information_schema.triggers
WHERE event_object_schema = 'ai_collab_audit_system'
ORDER BY trigger_name;

-- 16.7 验证 ENUM 定义（通过 SHOW COLUMNS）
SHOW COLUMNS FROM project_members WHERE Field = 'project_role';
SHOW COLUMNS FROM output_comments WHERE Field = 'status';
SHOW COLUMNS FROM issue_tags WHERE Field = 'severity';
SHOW COLUMNS FROM merge_records WHERE Field = 'merge_strategy';
SHOW COLUMNS FROM task_outputs WHERE Field = 'status';

-- ============================================================
-- 测试17：验证外键约束存在
-- ============================================================

SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    kcuReferenced.table_name AS referenced_table,
    kcuReferenced.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.key_column_usage kcuReferenced
    ON tc.constraint_name = kcuReferenced.constraint_name
    AND tc.table_schema = kcuReferenced.table_schema
    AND kcu.position_in_unique_constraint = kcuReferenced.position_in_unique_constraint
WHERE tc.table_schema = 'ai_collab_audit_system'
  AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, tc.constraint_name;

-- ============================================================
-- 测试18：验证 idx_tasks_creator 无重复（仅存在一次）
-- ============================================================
SELECT
    table_name,
    index_name,
    COUNT(*) AS index_count
FROM information_schema.statistics
WHERE table_schema = 'ai_collab_audit_system'
  AND index_name = 'idx_tasks_creator'
GROUP BY table_name, index_name;

-- ============================================================
-- 测试19：验证 user_roles 完整审计字段
-- ============================================================
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system'
  AND table_name = 'user_roles'
  AND column_name IN (
    'is_deleted', 'deleted_at', 'deleted_by',
    'created_at', 'created_by', 'updated_at', 'updated_by'
  )
ORDER BY column_name;

-- ============================================================
-- 测试20：验证 role_permissions 完整审计字段
-- ============================================================
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system'
  AND table_name = 'role_permissions'
  AND column_name IN (
    'is_deleted', 'deleted_at', 'deleted_by',
    'created_at', 'created_by', 'updated_at', 'updated_by'
  )
ORDER BY column_name;

-- ============================================================
-- 测试21：验证 output_issue_relations 完整审计字段
-- ============================================================
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'ai_collab_audit_system'
  AND table_name = 'output_issue_relations'
  AND column_name IN (
    'is_deleted', 'deleted_at', 'deleted_by',
    'created_at', 'created_by', 'updated_at', 'updated_by'
  )
ORDER BY column_name;

-- ============================================================
-- 测试22：验证所有索引无重复（GROUP BY 排除主键后计数>1即为重复）
-- ============================================================
SELECT table_name, index_name, COUNT(*) AS cnt
FROM information_schema.statistics
WHERE table_schema = 'ai_collab_audit_system'
  AND index_name != 'PRIMARY'
GROUP BY table_name, index_name
HAVING cnt > 1;
