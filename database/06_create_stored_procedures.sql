-- ============================================================
-- 06_create_stored_procedures.sql
-- AI-Collab-Audit-System - 存储过程和触发器创建脚本
--
-- 状态枚举值（严格遵守 Schema）：
--   task_outputs.status:
--     draft/generated/submitted/approved/rejected/revision_required/adopted/conflict_pending
--   project_tasks.status:
--     draft/running/generated/submitted/approved/rejected/revision_required/adopted/archived/conflict_pending
--   task_branches.status:
--     active/merged/closed/conflict_pending
--   merge_records.merge_strategy:
--     adopt_source/adopt_target/manual_merge/adopt_separately
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 触发器1：审核通过 -> 自动写入 operation_logs
-- 当 output_reviews.review_status = 'approved' 时触发
-- ============================================================

DROP TRIGGER IF EXISTS `trg_output_review_approved`;

DELIMITER //

CREATE TRIGGER `trg_output_review_approved`
AFTER INSERT ON `output_reviews`
FOR EACH ROW
BEGIN
    IF NEW.`review_status` = 'approved' THEN
        INSERT INTO `operation_logs` (
            `user_id`, `project_id`, `task_id`,
            `target_type`, `target_id`,
            `action_type`, `action_desc`, `new_value`, `created_at`
        )
        VALUES (
            NEW.`reviewer_id`,
            (SELECT `project_id` FROM `review_requests` WHERE `request_id` = NEW.`request_id`),
            (SELECT `task_id` FROM `review_requests` WHERE `request_id` = NEW.`request_id`),
            'output_reviews',
            NEW.`review_id`,
            'review_approved',
            CONCAT(
                '审核通过：输出 #', NEW.`output_id`,
                '，准确性 ', IFNULL(NEW.`accuracy_score`, 'N/A'),
                '，完整性 ', IFNULL(NEW.`completeness_score`, 'N/A'),
                '，逻辑性 ', IFNULL(NEW.`logic_score`, 'N/A'),
                '，规范性 ', IFNULL(NEW.`format_score`, 'N/A'),
                '，可用性 ', IFNULL(NEW.`usability_score`, 'N/A'),
                '，风险评分 ', IFNULL(NEW.`risk_score`, 'N/A')
            ),
            CONCAT(
                '{"review_id":', NEW.`review_id`,
                ',"output_id":', NEW.`output_id`,
                ',"reviewer_id":', NEW.`reviewer_id`,
                ',"review_status":"approved"',
                ',"accuracy_score":', IFNULL(NEW.`accuracy_score`, 'null'),
                ',"completeness_score":', IFNULL(NEW.`completeness_score`, 'null'),
                ',"logic_score":', IFNULL(NEW.`logic_score`, 'null'),
                ',"format_score":', IFNULL(NEW.`format_score`, 'null'),
                ',"usability_score":', IFNULL(NEW.`usability_score`, 'null'),
                ',"risk_score":', IFNULL(NEW.`risk_score`, 'null'),
                ',"review_comment":"', IFNULL(LEFT(NEW.`review_comment`, 200), ''), '"}'
            ),
            NEW.`reviewed_at`
        );
    END IF;
END//

DELIMITER ;

-- ============================================================
-- 触发器2：审核拒绝 -> 自动写入 operation_logs
-- 当 output_reviews.review_status = 'rejected' 时触发
-- ============================================================

DROP TRIGGER IF EXISTS `trg_output_review_rejected`;

DELIMITER //

CREATE TRIGGER `trg_output_review_rejected`
AFTER INSERT ON `output_reviews`
FOR EACH ROW
BEGIN
    IF NEW.`review_status` = 'rejected' THEN
        INSERT INTO `operation_logs` (
            `user_id`, `project_id`, `task_id`,
            `target_type`, `target_id`,
            `action_type`, `action_desc`, `new_value`, `created_at`
        )
        VALUES (
            NEW.`reviewer_id`,
            (SELECT `project_id` FROM `review_requests` WHERE `request_id` = NEW.`request_id`),
            (SELECT `task_id` FROM `review_requests` WHERE `request_id` = NEW.`request_id`),
            'output_reviews',
            NEW.`review_id`,
            'review_rejected',
            CONCAT('审核拒绝：输出 #', NEW.`output_id`, '，原因：', LEFT(IFNULL(NEW.`review_comment`, '未说明'), 200)),
            CONCAT(
                '{"review_id":', NEW.`review_id`,
                ',"output_id":', NEW.`output_id`,
                ',"reviewer_id":', NEW.`reviewer_id`,
                ',"review_status":"rejected"',
                ',"review_comment":"', IFNULL(LEFT(NEW.`review_comment`, 200), ''), '"}'
            ),
            NEW.`reviewed_at`
        );
    END IF;
END//

DELIMITER ;

-- ============================================================
-- 触发器3：审核退回 -> 自动写入 operation_logs
-- 当 output_reviews.review_status = 'revision_required' 时触发
-- ============================================================

DROP TRIGGER IF EXISTS `trg_output_review_revision_required`;

DELIMITER //

CREATE TRIGGER `trg_output_review_revision_required`
AFTER INSERT ON `output_reviews`
FOR EACH ROW
BEGIN
    IF NEW.`review_status` = 'revision_required' THEN
        INSERT INTO `operation_logs` (
            `user_id`, `project_id`, `task_id`,
            `target_type`, `target_id`,
            `action_type`, `action_desc`, `new_value`, `created_at`
        )
        VALUES (
            NEW.`reviewer_id`,
            (SELECT `project_id` FROM `review_requests` WHERE `request_id` = NEW.`request_id`),
            (SELECT `task_id` FROM `review_requests` WHERE `request_id` = NEW.`request_id`),
            'output_reviews',
            NEW.`review_id`,
            'review_revision_required',
            CONCAT('审核退回：输出 #', NEW.`output_id`, '，原因：', LEFT(IFNULL(NEW.`review_comment`, '未说明'), 200)),
            CONCAT(
                '{"review_id":', NEW.`review_id`,
                ',"output_id":', NEW.`output_id`,
                ',"reviewer_id":', NEW.`reviewer_id`,
                ',"review_status":"revision_required"',
                ',"review_comment":"', IFNULL(LEFT(NEW.`review_comment`, 200), ''), '"}'
            ),
            NEW.`reviewed_at`
        );
    END IF;
END//

DELIMITER ;

-- ============================================================
-- 存储过程1：sp_archive_project
-- 项目一键归档
-- 操作：
--   1. projects.status = 'archived'
--   2. project_tasks.status = 'archived'
--   3. task_branches.status = 'closed'
--   4. 写入 operation_logs
--   5. 事务保证一致性
-- ============================================================

DROP PROCEDURE IF EXISTS `sp_archive_project`;

DELIMITER //

CREATE PROCEDURE `sp_archive_project`(
    IN  p_project_id       INT UNSIGNED,
    IN  p_operator_id      INT UNSIGNED,
    OUT p_result_code      INT,
    OUT p_result_message   VARCHAR(255)
)
BEGIN
    DECLARE v_project_name    VARCHAR(200);
    DECLARE v_tasks_count     INT UNSIGNED DEFAULT 0;
    DECLARE v_branches_count INT UNSIGNED DEFAULT 0;
    DECLARE v_error_msg      VARCHAR(500);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_code = 500;
        GET DIAGNOSTICS CONDITION 1 v_error_msg = MESSAGE_TEXT;
        SET p_result_message = CONCAT('归档失败：', v_error_msg);
    END;

    START TRANSACTION;

    SELECT `project_name` INTO v_project_name
    FROM `projects`
    WHERE `project_id` = p_project_id AND `is_deleted` = 0
    FOR UPDATE;

    IF v_project_name IS NULL THEN
        ROLLBACK;
        SET p_result_code = 404;
        SET p_result_message = '项目不存在';
    ELSE
        UPDATE `projects`
        SET `status` = 'archived',
            `updated_at` = NOW(),
            `updated_by` = p_operator_id
        WHERE `project_id` = p_project_id;

        SELECT COUNT(*) INTO v_tasks_count
        FROM `project_tasks`
        WHERE `project_id` = p_project_id AND `is_deleted` = 0;

        SELECT COUNT(*) INTO v_branches_count
        FROM `task_branches`
        WHERE `project_id` = p_project_id AND `is_deleted` = 0;

        -- 项目任务全部归档
        UPDATE `project_tasks`
        SET `status` = 'archived',
            `updated_at` = NOW(),
            `updated_by` = p_operator_id
        WHERE `project_id` = p_project_id AND `is_deleted` = 0;

        -- 项目分支全部关闭
        UPDATE `task_branches`
        SET `status` = 'closed',
            `updated_at` = NOW(),
            `updated_by` = p_operator_id
        WHERE `project_id` = p_project_id AND `is_deleted` = 0;

        INSERT INTO `operation_logs` (
            `user_id`, `project_id`, `target_type`, `target_id`,
            `action_type`, `action_desc`, `old_value`, `new_value`, `created_at`
        ) VALUES (
            p_operator_id, p_project_id,
            'projects', p_project_id,
            'project_archive',
            CONCAT('项目归档：', v_project_name, '，归档任务数：', v_tasks_count, '，分支数：', v_branches_count),
            '{"status":"active"}',
            CONCAT('{"status":"archived","archived_tasks":', v_tasks_count, ',"archived_branches":', v_branches_count, '}'),
            NOW()
        );

        COMMIT;
        SET p_result_code = 0;
        SET p_result_message = CONCAT('项目归档成功，归档任务数：', v_tasks_count, '，分支数：', v_branches_count);
    END IF;
END//

DELIMITER ;

-- ============================================================
-- 存储过程2：sp_create_project_with_owner
-- 创建项目并自动将创建人添加为成员（角色 leader）
-- ============================================================

DROP PROCEDURE IF EXISTS `sp_create_project_with_owner`;

DELIMITER //

CREATE PROCEDURE `sp_create_project_with_owner`(
    IN  p_project_name     VARCHAR(200),
    IN  p_project_type     VARCHAR(50),
    IN  p_description     TEXT,
    IN  p_owner_id         INT UNSIGNED,
    IN  p_operator_id      INT UNSIGNED,
    OUT p_result_code      INT,
    OUT p_result_message   VARCHAR(255),
    OUT p_new_project_id   INT UNSIGNED
)
BEGIN
    DECLARE v_error_msg VARCHAR(500);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_code = 500;
        GET DIAGNOSTICS CONDITION 1 v_error_msg = MESSAGE_TEXT;
        SET p_result_message = CONCAT('创建项目失败：', v_error_msg);
    END;

    START TRANSACTION;

    INSERT INTO `projects` (
        `project_name`, `project_type`, `description`,
        `owner_id`, `status`, `created_by`, `created_at`
    ) VALUES (
        p_project_name, p_project_type, p_description,
        p_owner_id, 'active', p_operator_id, NOW()
    );

    SET p_new_project_id = LAST_INSERT_ID();

    INSERT INTO `project_members` (
        `project_id`, `user_id`, `project_role`,
        `status`, `joined_at`, `created_by`, `created_at`
    ) VALUES (
        p_new_project_id, p_owner_id, 'leader',
        'active', NOW(), p_operator_id, NOW()
    );

    INSERT INTO `operation_logs` (
        `user_id`, `project_id`, `target_type`, `target_id`,
        `action_type`, `action_desc`, `new_value`, `created_at`
    ) VALUES (
        p_operator_id, p_new_project_id,
        'projects', p_new_project_id,
        'project_create',
        CONCAT('创建项目：', p_project_name),
        CONCAT('{"project_id":', p_new_project_id, ',"project_name":"', p_project_name, '"}'),
        NOW()
    );

    COMMIT;
    SET p_result_code = 0;
    SET p_result_message = '项目创建成功';
END//

DELIMITER ;

-- ============================================================
-- 存储过程3：sp_submit_output_for_review
-- 提交输出版本进行审核
-- 操作：
--   1. task_outputs.status = 'submitted'
--   2. 插入 review_requests
--   3. project_tasks.status = 'submitted'
--   4. 写入 operation_logs
--   5. 事务保证一致性
-- ============================================================

DROP PROCEDURE IF EXISTS `sp_submit_output_for_review`;

DELIMITER //

CREATE PROCEDURE `sp_submit_output_for_review`(
    IN  p_output_id       INT UNSIGNED,
    IN  p_reviewer_id     INT UNSIGNED,
    IN  p_submit_note     TEXT,
    IN  p_submitter_id    INT UNSIGNED,
    OUT p_result_code     INT,
    OUT p_result_message  VARCHAR(255),
    OUT p_new_request_id  INT UNSIGNED
)
BEGIN
    DECLARE v_task_id      INT UNSIGNED;
    DECLARE v_project_id   INT UNSIGNED;
    DECLARE v_output_title VARCHAR(200);
    DECLARE v_error_msg   VARCHAR(500);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_code = 500;
        GET DIAGNOSTICS CONDITION 1 v_error_msg = MESSAGE_TEXT;
        SET p_result_message = CONCAT('提交审核失败：', v_error_msg);
    END;

    START TRANSACTION;

    SELECT `task_id`, `output_title`
    INTO v_task_id, v_output_title
    FROM `task_outputs`
    WHERE `output_id` = p_output_id AND `is_deleted` = 0
    FOR UPDATE;

    IF v_task_id IS NULL THEN
        ROLLBACK;
        SET p_result_code = 404;
        SET p_result_message = '输出版本不存在';
    ELSE
        SELECT `project_id` INTO v_project_id
        FROM `project_tasks`
        WHERE `task_id` = v_task_id AND `is_deleted` = 0;

        UPDATE `task_outputs`
        SET `is_final_candidate` = 0,
            `updated_at` = NOW(),
            `updated_by` = p_submitter_id
        WHERE `task_id` = v_task_id AND `is_deleted` = 0;

        UPDATE `task_outputs`
        SET `is_final_candidate` = 1,
            `status` = 'submitted',
            `updated_at` = NOW(),
            `updated_by` = p_submitter_id
        WHERE `output_id` = p_output_id;

        INSERT INTO `review_requests` (
            `output_id`, `task_id`, `project_id`,
            `submitter_id`, `reviewer_id`,
            `request_status`, `submit_note`,
            `created_by`, `created_at`
        ) VALUES (
            p_output_id, v_task_id, v_project_id,
            p_submitter_id, p_reviewer_id,
            'pending', p_submit_note,
            p_submitter_id, NOW()
        );

        SET p_new_request_id = LAST_INSERT_ID();

        UPDATE `project_tasks`
        SET `status` = 'submitted',
            `updated_at` = NOW(),
            `updated_by` = p_submitter_id
        WHERE `task_id` = v_task_id AND `is_deleted` = 0;

        INSERT INTO `operation_logs` (
            `user_id`, `project_id`, `task_id`,
            `target_type`, `target_id`,
            `action_type`, `action_desc`,
            `new_value`, `created_at`
        ) VALUES (
            p_submitter_id, v_project_id, v_task_id,
            'review_requests', p_new_request_id,
            'submit_review',
            CONCAT('提交审核：输出 #', p_output_id, ' - ', v_output_title),
            CONCAT(
                '{"request_id":', p_new_request_id,
                ',"output_id":', p_output_id,
                ',"reviewer_id":', p_reviewer_id,
                ',"submit_note":"', IFNULL(LEFT(p_submit_note, 200), ''), '"}'
            ),
            NOW()
        );

        COMMIT;
        SET p_result_code = 0;
        SET p_result_message = '提交审核成功';
    END IF;
END//

DELIMITER ;

-- ============================================================
-- 存储过程4：sp_complete_review
-- 完成审核（通过/拒绝/退回）
-- 操作：
--   1. 更新 output_reviews 审核记录
--   2. 更新 review_requests.request_status
--   3. 更新 task_outputs.status（根据审核结论）
--   4. 更新 project_tasks.status（根据审核结论）
--   5. 写入 output_issue_relations（问题标签关联）
--   6. 事务保证一致性
-- ============================================================

DROP PROCEDURE IF EXISTS `sp_complete_review`;

DELIMITER //

CREATE PROCEDURE `sp_complete_review`(
    IN  p_request_id        INT UNSIGNED,
    IN  p_reviewer_id       INT UNSIGNED,
    IN  p_review_status     VARCHAR(30),
    IN  p_accuracy_score    DECIMAL(3,1),
    IN  p_completeness_score DECIMAL(3,1),
    IN  p_logic_score       DECIMAL(3,1),
    IN  p_format_score      DECIMAL(3,1),
    IN  p_usability_score   DECIMAL(3,1),
    IN  p_risk_score        DECIMAL(3,1),
    IN  p_review_comment     TEXT,
    IN  p_issue_tag_ids     TEXT,
    OUT p_result_code       INT,
    OUT p_result_message    VARCHAR(255),
    OUT p_new_review_id     INT UNSIGNED
)
BEGIN
    DECLARE v_output_id    INT UNSIGNED;
    DECLARE v_task_id      INT UNSIGNED;
    DECLARE v_project_id   INT UNSIGNED;
    DECLARE v_tag_id       INT UNSIGNED;
    DECLARE v_pos          INT DEFAULT 1;
    DECLARE v_len          INT;
    DECLARE v_error_msg    VARCHAR(500);

    -- 显式校验审核结论值（防止非法状态写入数据库）
    IF p_review_status NOT IN ('approved', 'rejected', 'revision_required') THEN
        SET p_result_code = 400;
        SET p_result_message = CONCAT('非法审核结论：', p_review_status, '，允许值：approved/rejected/revision_required');
    ELSE
        START TRANSACTION;

        SELECT `output_id`, `task_id`, `project_id`
        INTO v_output_id, v_task_id, v_project_id
        FROM `review_requests`
        WHERE `request_id` = p_request_id AND `is_deleted` = 0
        FOR UPDATE;

        IF v_output_id IS NULL THEN
            ROLLBACK;
            SET p_result_code = 404;
            SET p_result_message = '审核请求不存在';
        ELSE
        INSERT INTO `output_reviews` (
            `request_id`, `output_id`, `reviewer_id`,
            `accuracy_score`, `completeness_score`, `logic_score`,
            `format_score`, `usability_score`, `risk_score`,
            `review_status`, `review_comment`,
            `reviewed_at`, `created_by`, `created_at`
        ) VALUES (
            p_request_id, v_output_id, p_reviewer_id,
            p_accuracy_score, p_completeness_score, p_logic_score,
            p_format_score, p_usability_score, p_risk_score,
            p_review_status, p_review_comment,
            NOW(), p_reviewer_id, NOW()
        );

        SET p_new_review_id = LAST_INSERT_ID();

        UPDATE `review_requests`
        SET `request_status` = p_review_status,
            `reviewed_at` = NOW(),
            `updated_at` = NOW(),
            `updated_by` = p_reviewer_id
        WHERE `request_id` = p_request_id;

        -- 根据审核结论更新 task_outputs.status
        UPDATE `task_outputs`
        SET `status` = p_review_status,
            `updated_at` = NOW(),
            `updated_by` = p_reviewer_id
        WHERE `output_id` = v_output_id;

        -- 根据审核结论更新 project_tasks.status
        UPDATE `project_tasks`
        SET `status` = p_review_status,
            `updated_at` = NOW(),
            `updated_by` = p_reviewer_id
        WHERE `task_id` = v_task_id AND `is_deleted` = 0;

        -- 写入问题标签关联（p_issue_tag_ids 为逗号分隔的标签ID，如 "1,3,5"）
        IF p_issue_tag_ids IS NOT NULL AND LENGTH(p_issue_tag_ids) > 0 THEN
            SET v_len = LENGTH(p_issue_tag_ids);
            WHILE v_pos <= v_len DO
                SET v_tag_id = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(p_issue_tag_ids, ',', v_pos), ',', -1) AS UNSIGNED);
                IF v_tag_id > 0 THEN
                    INSERT IGNORE INTO `output_issue_relations`
                        (`output_id`, `review_id`, `tag_id`, `created_by`, `created_at`)
                    VALUES
                        (v_output_id, p_new_review_id, v_tag_id, p_reviewer_id, NOW());
                END IF;
                SET v_pos = v_pos + 1;
            END WHILE;
        END IF;

        INSERT INTO `operation_logs` (
            `user_id`, `project_id`, `task_id`,
            `target_type`, `target_id`,
            `action_type`, `action_desc`,
            `new_value`, `created_at`
        ) VALUES (
            p_reviewer_id, v_project_id, v_task_id,
            'output_reviews', p_new_review_id,
            CONCAT('review_', p_review_status),
            CONCAT('完成审核（', p_review_status, '）：输出 #', v_output_id),
            CONCAT(
                '{"review_id":', p_new_review_id,
                ',"output_id":', v_output_id,
                ',"review_status":"', p_review_status, '"',
                ',"accuracy_score":', IFNULL(p_accuracy_score, 'null'),
                ',"completeness_score":', IFNULL(p_completeness_score, 'null'),
                ',"logic_score":', IFNULL(p_logic_score, 'null'),
                ',"format_score":', IFNULL(p_format_score, 'null'),
                ',"usability_score":', IFNULL(p_usability_score, 'null'),
                ',"risk_score":', IFNULL(p_risk_score, 'null'),
                ',"review_comment":"', IFNULL(LEFT(p_review_comment, 200), ''), '"}'
            ),
            NOW()
        );

        COMMIT;
        SET p_result_code = 0;
        SET p_result_message = CONCAT('审核完成（', p_review_status, '）');
    END IF;
END//

DELIMITER ;

-- ============================================================
-- 存储过程5：sp_adopt_output
-- 采用输出为项目成果
-- 操作：
--   1. 在 adopted_outputs 插入采用记录
--   2. task_outputs.status = 'adopted'
--   3. project_tasks.status = 'adopted'
--   4. 写入 operation_logs
--   5. 事务保证一致性
-- ============================================================

DROP PROCEDURE IF EXISTS `sp_adopt_output`;

DELIMITER //

CREATE PROCEDURE `sp_adopt_output`(
    IN  p_output_id          INT UNSIGNED,
    IN  p_artifact_title     VARCHAR(200),
    IN  p_artifact_type     VARCHAR(50),
    IN  p_release_version   VARCHAR(50),
    IN  p_adopter_id       INT UNSIGNED,
    OUT p_result_code       INT,
    OUT p_result_message    VARCHAR(255),
    OUT p_new_adopted_id    INT UNSIGNED
)
BEGIN
    DECLARE v_task_id      INT UNSIGNED;
    DECLARE v_project_id   INT UNSIGNED;
    DECLARE v_output_title VARCHAR(200);
    DECLARE v_error_msg    VARCHAR(500);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_code = 500;
        GET DIAGNOSTICS CONDITION 1 v_error_msg = MESSAGE_TEXT;
        SET p_result_message = CONCAT('采用成果失败：', v_error_msg);
    END;

    START TRANSACTION;

    SELECT `task_id`, `output_title`
    INTO v_task_id, v_output_title
    FROM `task_outputs`
    WHERE `output_id` = p_output_id AND `is_deleted` = 0
    FOR UPDATE;

    IF v_task_id IS NULL THEN
        ROLLBACK;
        SET p_result_code = 404;
        SET p_result_message = '输出版本不存在';
    ELSE
        SELECT `project_id` INTO v_project_id
        FROM `project_tasks`
        WHERE `task_id` = v_task_id AND `is_deleted` = 0;

        INSERT INTO `adopted_outputs` (
            `project_id`, `task_id`, `output_id`,
            `artifact_title`, `artifact_type`, `release_version`,
            `adopted_by`, `adopted_at`,
            `created_by`, `created_at`
        ) VALUES (
            v_project_id, v_task_id, p_output_id,
            COALESCE(p_artifact_title, v_output_title),
            p_artifact_type, p_release_version,
            p_adopter_id, NOW(),
            p_adopter_id, NOW()
        );

        SET p_new_adopted_id = LAST_INSERT_ID();

        UPDATE `task_outputs`
        SET `status` = 'adopted',
            `updated_at` = NOW(),
            `updated_by` = p_adopter_id
        WHERE `output_id` = p_output_id;

        UPDATE `project_tasks`
        SET `status` = 'adopted',
            `updated_at` = NOW(),
            `updated_by` = p_adopter_id
        WHERE `task_id` = v_task_id AND `is_deleted` = 0;

        INSERT INTO `operation_logs` (
            `user_id`, `project_id`, `task_id`,
            `target_type`, `target_id`,
            `action_type`, `action_desc`,
            `new_value`, `created_at`
        ) VALUES (
            p_adopter_id, v_project_id, v_task_id,
            'adopted_outputs', p_new_adopted_id,
            'output_adopt',
            CONCAT('采用成果：输出 #', p_output_id, ' - ', COALESCE(p_artifact_title, v_output_title)),
            CONCAT(
                '{"adopted_id":', p_new_adopted_id,
                ',"output_id":', p_output_id,
                ',"artifact_title":"', COALESCE(p_artifact_title, v_output_title),
                '","artifact_type":"', IFNULL(p_artifact_type, ''), '"}'
            ),
            NOW()
        );

        COMMIT;
        SET p_result_code = 0;
        SET p_result_message = '采用成果成功';
    END IF;
END//

DELIMITER ;
