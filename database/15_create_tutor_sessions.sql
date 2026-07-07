-- ============================================================
-- 15_create_tutor_sessions.sql
-- EduAgent Studio - 模块六：Tutor Chat 答疑会话表
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- Tutor Sessions 表：存储学生答疑会话记录
-- ============================================================
CREATE TABLE IF NOT EXISTS `tutor_sessions` (
    `session_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '会话ID',
    `profile_id` INT UNSIGNED NOT NULL COMMENT '学生画像ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '课程ID',
    `question` TEXT NOT NULL COMMENT '学生问题',
    `answer` TEXT NULL COMMENT 'Tutor回答',
    `explanation_level` VARCHAR(20) NULL COMMENT '解释级别：basic/intermediate/advanced',
    `helpful` TINYINT DEFAULT NULL COMMENT '是否有用：1=有用，0=没用，NULL=未评价',
    `follow_up` TEXT NULL COMMENT '追问内容',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    PRIMARY KEY (`session_id`),
    KEY `idx_profile_id` (`profile_id`),
    KEY `idx_course_id` (`course_id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Tutor 答疑会话表';
