-- ============================================================
-- 05_create_views.sql
-- AI-Collab-Audit-System - 视图创建脚本
-- task_outputs.status 枚举值：draft/generated/submitted/approved/rejected/revision_required/adopted/conflict_pending
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 视图1：项目任务统计视图
-- ============================================================
DROP VIEW IF EXISTS `v_project_task_statistics`;

CREATE
VIEW `v_project_task_statistics` AS
SELECT
    p.`project_id`                                       AS `project_id`,
    p.`project_name`                                    AS `project_name`,
    p.`project_type`                                     AS `project_type`,
    p.`owner_id`                                         AS `owner_id`,
    u.`real_name`                                        AS `owner_name`,
    p.`status`                                           AS `project_status`,
    p.`created_at`                                       AS `project_created_at`,

    COUNT(DISTINCT t.`task_id`)                         AS `total_tasks`,
    SUM(CASE WHEN t.`status` = 'draft'             THEN 1 ELSE 0 END) AS `task_draft`,
    SUM(CASE WHEN t.`status` = 'running'            THEN 1 ELSE 0 END) AS `task_running`,
    SUM(CASE WHEN t.`status` = 'generated'          THEN 1 ELSE 0 END) AS `task_generated`,
    SUM(CASE WHEN t.`status` = 'submitted'          THEN 1 ELSE 0 END) AS `task_submitted`,
    SUM(CASE WHEN t.`status` = 'approved'           THEN 1 ELSE 0 END) AS `task_approved`,
    SUM(CASE WHEN t.`status` = 'rejected'           THEN 1 ELSE 0 END) AS `task_rejected`,
    SUM(CASE WHEN t.`status` = 'revision_required'  THEN 1 ELSE 0 END) AS `task_revision_required`,
    SUM(CASE WHEN t.`status` = 'adopted'             THEN 1 ELSE 0 END) AS `task_adopted`,
    SUM(CASE WHEN t.`status` = 'archived'           THEN 1 ELSE 0 END) AS `task_archived`,
    SUM(CASE WHEN t.`status` = 'conflict_pending'   THEN 1 ELSE 0 END) AS `task_conflict_pending`,

    COUNT(DISTINCT pm.`member_id`)                      AS `total_members`,
    COUNT(DISTINCT o.`output_id`)                        AS `total_outputs`,
    COUNT(DISTINCT rr.`request_id`)                      AS `total_review_requests`,
    SUM(CASE WHEN rr.`request_status` = 'pending'  THEN 1 ELSE 0 END) AS `pending_reviews`,
    COUNT(DISTINCT ao.`adopted_id`)                     AS `total_adopted`

FROM `projects` p
LEFT JOIN `users` u
    ON p.`owner_id` = u.`user_id` AND u.`is_deleted` = 0
LEFT JOIN `project_tasks` t
    ON p.`project_id` = t.`project_id` AND t.`is_deleted` = 0
LEFT JOIN `project_members` pm
    ON p.`project_id` = pm.`project_id` AND pm.`is_deleted` = 0
LEFT JOIN `task_outputs` o
    ON t.`task_id` = o.`task_id` AND o.`is_deleted` = 0
LEFT JOIN `review_requests` rr
    ON p.`project_id` = rr.`project_id` AND rr.`is_deleted` = 0
LEFT JOIN `adopted_outputs` ao
    ON p.`project_id` = ao.`project_id` AND ao.`is_deleted` = 0
WHERE p.`is_deleted` = 0
GROUP BY
    p.`project_id`, p.`project_name`, p.`project_type`,
    p.`owner_id`, u.`real_name`, p.`status`, p.`created_at`
ORDER BY p.`created_at` DESC;

-- ============================================================
-- 视图2：模型调用统计视图
-- ============================================================
DROP VIEW IF EXISTS `v_model_invocation_statistics`;

CREATE
VIEW `v_model_invocation_statistics` AS
SELECT
    m.`model_id`                                        AS `model_id`,
    m.`model_name`                                      AS `model_name`,
    m.`display_name`                                    AS `display_name`,
    m.`provider_id`                                     AS `provider_id`,
    mp.`provider_name`                                  AS `provider_name`,
    m.`status`                                          AS `model_status`,

    COUNT(DISTINCT ai.`invocation_id`)                  AS `total_invocations`,
    SUM(CASE WHEN ai.`status` = 'success'  THEN 1 ELSE 0 END) AS `success_count`,
    SUM(CASE WHEN ai.`status` = 'failed'    THEN 1 ELSE 0 END) AS `failed_count`,
    SUM(CASE WHEN ai.`status` = 'timeout'   THEN 1 ELSE 0 END) AS `timeout_count`,
    SUM(CASE WHEN ai.`status` = 'blocked'   THEN 1 ELSE 0 END) AS `blocked_count`,

    COALESCE(SUM(ai.`input_tokens`), 0)                 AS `total_input_tokens`,
    COALESCE(SUM(ai.`output_tokens`), 0)                AS `total_output_tokens`,
    COALESCE(SUM(ai.`input_tokens`) + SUM(ai.`output_tokens`), 0) AS `total_tokens`,

    COALESCE(SUM(cr.`total_cost`), 0)                   AS `total_cost`,

    COALESCE(AVG(ai.`latency_ms`), 0)                  AS `avg_latency_ms`,
    COALESCE(MAX(ai.`latency_ms`), 0)                  AS `max_latency_ms`,
    COALESCE(MIN(CASE WHEN ai.`latency_ms` > 0 THEN ai.`latency_ms` END), 0) AS `min_latency_ms`,

    CASE
        WHEN COUNT(DISTINCT ai.`invocation_id`) > 0
        THEN ROUND(
            SUM(CASE WHEN ai.`status` = 'success' THEN 1 ELSE 0 END) * 100.0
            / COUNT(DISTINCT ai.`invocation_id`), 2)
        ELSE 0.00
    END                                                 AS `success_rate`,

    COALESCE(SUM(ai.`input_tokens`) / 1000.0 * m.`input_price`, 0) AS `estimated_input_cost`,
    COALESCE(SUM(ai.`output_tokens`) / 1000.0 * m.`output_price`, 0) AS `estimated_output_cost`

FROM `ai_models` m
LEFT JOIN `model_providers` mp
    ON m.`provider_id` = mp.`provider_id` AND mp.`is_deleted` = 0
LEFT JOIN `ai_invocations` ai
    ON m.`model_id` = ai.`model_id`
LEFT JOIN `cost_records` cr
    ON ai.`invocation_id` = cr.`invocation_id`
WHERE m.`is_deleted` = 0
GROUP BY
    m.`model_id`, m.`model_name`, m.`display_name`,
    m.`provider_id`, mp.`provider_name`, m.`status`
ORDER BY `total_invocations` DESC;

-- ============================================================
-- 视图3：待审核输出视图
-- ============================================================
DROP VIEW IF EXISTS `v_pending_reviews`;

CREATE
VIEW `v_pending_reviews` AS
SELECT
    rr.`request_id`                                     AS `request_id`,
    rr.`output_id`                                      AS `output_id`,
    rr.`task_id`                                        AS `task_id`,
    rr.`project_id`                                     AS `project_id`,
    rr.`submitter_id`                                   AS `submitter_id`,
    sub.`real_name`                                     AS `submitter_name`,
    rr.`reviewer_id`                                    AS `reviewer_id`,
    rev.`real_name`                                     AS `reviewer_name`,
    rr.`request_status`                                 AS `request_status`,
    rr.`submit_note`                                    AS `submit_note`,
    rr.`created_at`                                     AS `submit_time`,

    o.`output_title`                                    AS `output_title`,
    o.`source_type`                                     AS `source_type`,
    o.`version_no`                                      AS `version_no`,
    o.`content`                                         AS `content_preview`,

    t.`title`                                           AS `task_title`,
    p.`project_name`                                     AS `project_name`,

    u1.`real_name`                                      AS `output_creator`

FROM `review_requests` rr
INNER JOIN `task_outputs` o
    ON rr.`output_id` = o.`output_id` AND o.`is_deleted` = 0
INNER JOIN `project_tasks` t
    ON rr.`task_id` = t.`task_id` AND t.`is_deleted` = 0
INNER JOIN `projects` p
    ON rr.`project_id` = p.`project_id` AND p.`is_deleted` = 0
LEFT JOIN `users` sub
    ON rr.`submitter_id` = sub.`user_id` AND sub.`is_deleted` = 0
LEFT JOIN `users` rev
    ON rr.`reviewer_id` = rev.`user_id` AND rev.`is_deleted` = 0
LEFT JOIN `users` u1
    ON o.`created_by` = u1.`user_id` AND u1.`is_deleted` = 0
WHERE rr.`is_deleted` = 0
  AND rr.`request_status` = 'pending'
ORDER BY rr.`created_at` ASC;

-- ============================================================
-- 视图4：用户权限视图
-- ============================================================
DROP VIEW IF EXISTS `v_user_permissions`;

CREATE
VIEW `v_user_permissions` AS
SELECT
    u.`user_id`                                         AS `user_id`,
    u.`username`                                        AS `username`,
    u.`real_name`                                        AS `real_name`,
    u.`email`                                           AS `email`,
    u.`status`                                          AS `user_status`,

    GROUP_CONCAT(DISTINCT r.`role_name` ORDER BY r.`role_name` SEPARATOR ', ') AS `roles`,
    GROUP_CONCAT(DISTINCT r.`role_code` ORDER BY r.`role_code` SEPARATOR ',') AS `role_codes`,

    COUNT(DISTINCT rp.`permission_id`)                   AS `permission_count`,
    GROUP_CONCAT(DISTINCT p.`permission_name` ORDER BY p.`module_name`, p.`permission_name` SEPARATOR ', ') AS `permissions`,

    u.`last_login_at`                                    AS `last_login_at`,
    u.`created_at`                                       AS `created_at`

FROM `users` u
LEFT JOIN `user_roles` ur
    ON u.`user_id` = ur.`user_id` AND ur.`is_deleted` = 0
LEFT JOIN `roles` r
    ON ur.`role_id` = r.`role_id` AND r.`is_deleted` = 0
LEFT JOIN `role_permissions` rp
    ON r.`role_id` = rp.`role_id` AND rp.`is_deleted` = 0
LEFT JOIN `permissions` p
    ON rp.`permission_id` = p.`permission_id` AND p.`is_deleted` = 0
WHERE u.`is_deleted` = 0
GROUP BY
    u.`user_id`, u.`username`, u.`real_name`, u.`email`,
    u.`status`, u.`last_login_at`, u.`created_at`
ORDER BY u.`created_at` DESC;

-- ============================================================
-- 视图5：项目成果库视图
-- ============================================================
DROP VIEW IF EXISTS `v_artifacts`;

CREATE
VIEW `v_artifacts` AS
SELECT
    ao.`adopted_id`                                     AS `adopted_id`,
    ao.`project_id`                                      AS `project_id`,
    p.`project_name`                                     AS `project_name`,
    p.`project_type`                                     AS `project_type`,
    ao.`task_id`                                         AS `task_id`,
    t.`title`                                            AS `task_title`,
    ao.`output_id`                                       AS `output_id`,
    o.`output_title`                                     AS `output_title`,
    o.`version_no`                                       AS `version_no`,
    o.`content`                                          AS `content`,
    ao.`artifact_title`                                  AS `artifact_title`,
    ao.`artifact_type`                                   AS `artifact_type`,
    ao.`release_version`                                 AS `release_version`,
    ao.`adopted_by`                                      AS `adopted_by`,
    u.`real_name`                                        AS `adopted_by_name`,
    ao.`adopted_at`                                      AS `adopted_at`,
    p.`owner_id`                                         AS `project_owner_id`,
    ow.`real_name`                                       AS `project_owner_name`

FROM `adopted_outputs` ao
INNER JOIN `projects` p
    ON ao.`project_id` = p.`project_id` AND p.`is_deleted` = 0
INNER JOIN `project_tasks` t
    ON ao.`task_id` = t.`task_id` AND t.`is_deleted` = 0
INNER JOIN `task_outputs` o
    ON ao.`output_id` = o.`output_id` AND o.`is_deleted` = 0
INNER JOIN `users` u
    ON ao.`adopted_by` = u.`user_id` AND u.`is_deleted` = 0
INNER JOIN `users` ow
    ON p.`owner_id` = ow.`user_id` AND ow.`is_deleted` = 0
WHERE ao.`is_deleted` = 0
ORDER BY ao.`adopted_at` DESC;
