-- ============================================================
-- 09_create_a3_tables.sql
-- EduAgent Studio - A3 赛题专用表（课程/学生画像/知识点/学习资源等）
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 1. courses 课程表
-- ============================================================
CREATE TABLE IF NOT EXISTS `courses` (
    `course_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '课程ID',
    `course_name` VARCHAR(200) NOT NULL COMMENT '课程名称',
    `course_code` VARCHAR(50) NULL COMMENT '课程代码',
    `description` TEXT NULL COMMENT '课程描述',
    `teacher_id` INT UNSIGNED NOT NULL COMMENT '主讲教师ID',
    `status` ENUM('active','archived','draft') NOT NULL DEFAULT 'active' COMMENT '课程状态',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`course_id`),
    KEY `idx_courses_teacher` (`teacher_id`),
    KEY `idx_courses_status_deleted` (`status`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- ============================================================
-- 2. knowledge_points 知识点表
-- ============================================================
CREATE TABLE IF NOT EXISTS `knowledge_points` (
    `kp_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '知识点ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `kp_name` VARCHAR(200) NOT NULL COMMENT '知识点名称',
    `kp_code` VARCHAR(50) NULL COMMENT '知识点编码',
    `parent_kp_id` INT UNSIGNED NULL COMMENT '父知识点ID',
    `difficulty_level` ENUM('basic','intermediate','advanced') NOT NULL DEFAULT 'basic' COMMENT '难度等级',
    `description` TEXT NULL COMMENT '知识点描述',
    `estimated_hours` DECIMAL(5,2) NULL COMMENT '预计学习时长（小时）',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`kp_id`),
    KEY `idx_kp_course` (`course_id`),
    KEY `idx_kp_parent` (`parent_kp_id`),
    KEY `idx_kp_difficulty` (`difficulty_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点表';

-- ============================================================
-- 3. student_profiles 学生画像表
-- ============================================================
CREATE TABLE IF NOT EXISTS `student_profiles` (
    `profile_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '画像ID',
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生用户ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `learning_goal` TEXT NULL COMMENT '学习目标',
    `knowledge_base` TEXT NULL COMMENT '已有知识基础',
    `current_level` TEXT NULL COMMENT '当前基础水平',
    `cognitive_style` VARCHAR(100) NULL COMMENT '认知与学习风格',
    `time_constraints` VARCHAR(255) NULL COMMENT '学习时间约束描述',
    `practice_level` VARCHAR(100) NULL COMMENT '实践能力水平',
    `motivation` VARCHAR(255) NULL COMMENT '学习动机',
    `error_prone_points` JSON NULL COMMENT '易错点列表',
    `interests` VARCHAR(500) NULL COMMENT '兴趣方向',
    `resource_preferences` VARCHAR(500) NULL COMMENT '资源类型偏好',
    `weekly_hours` INT UNSIGNED NULL COMMENT '每周可用于学习的小时数',
    `mastery_score` DECIMAL(5,3) NOT NULL DEFAULT 0.000 COMMENT '综合掌握度评分（0-1）',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`profile_id`),
    UNIQUE KEY `uk_student_course` (`student_id`, `course_id`),
    KEY `idx_profile_course` (`course_id`),
    KEY `idx_profile_mastery` (`mastery_score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生画像表';

-- ============================================================
-- 4. student_knowledge_mastery 学生知识点掌握度表
-- ============================================================
CREATE TABLE IF NOT EXISTS `student_knowledge_mastery` (
    `mastery_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '掌握度记录ID',
    `profile_id` INT UNSIGNED NOT NULL COMMENT '画像ID',
    `kp_id` INT UNSIGNED NOT NULL COMMENT '知识点ID',
    `mastery_level` DECIMAL(5,3) NOT NULL DEFAULT 0.000 COMMENT '掌握度评分（0-1）',
    `last_test_score` DECIMAL(5,3) NULL COMMENT '最近一次测验得分（0-1）',
    `last_test_date` DATE NULL COMMENT '最近测验日期',
    `update_reason` VARCHAR(255) NULL COMMENT '更新原因',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`mastery_id`),
    UNIQUE KEY `uk_profile_kp` (`profile_id`, `kp_id`),
    KEY `idx_mastery_kp` (`kp_id`),
    KEY `idx_mastery_level` (`mastery_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生知识点掌握度表';

-- ============================================================
-- 5. learning_resources 学习资源表
-- ============================================================
CREATE TABLE IF NOT EXISTS `learning_resources` (
    `resource_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '资源ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `resource_title` VARCHAR(200) NOT NULL COMMENT '资源标题',
    `resource_type` ENUM('lecture','ppt','quiz','case','review','test','other') NOT NULL COMMENT '资源类型',
    `difficulty` ENUM('basic','intermediate','advanced') NOT NULL DEFAULT 'basic' COMMENT '难度等级',
    `content` LONGTEXT NULL COMMENT '资源正文内容',
    `target_kp_ids` VARCHAR(500) NULL COMMENT '关联知识点ID列表',
    `generation_model` VARCHAR(100) NULL COMMENT '生成所用模型',
    `generation_agent` VARCHAR(100) NULL COMMENT '生成所用智能体',
    `invocation_id` BIGINT UNSIGNED NULL COMMENT '关联的AI调用记录ID',
    `status` ENUM('draft','pending_review','approved','rejected','archived') NOT NULL DEFAULT 'draft' COMMENT '审核状态',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`resource_id`),
    KEY `idx_resource_course` (`course_id`),
    KEY `idx_resource_type` (`resource_type`),
    KEY `idx_resource_status` (`status`, `is_deleted`),
    KEY `idx_resource_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习资源表';

-- ============================================================
-- 6. learning_feedbacks 学习反馈表
-- ============================================================
CREATE TABLE IF NOT EXISTS `learning_feedbacks` (
    `feedback_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '反馈ID',
    `profile_id` INT UNSIGNED NOT NULL COMMENT '学生画像ID',
    `resource_id` INT UNSIGNED NULL COMMENT '关联学习资源ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '课程ID',
    `feedback_type` ENUM('quiz_result','self_report','study_note','question') NOT NULL COMMENT '反馈类型',
    `content` TEXT NULL COMMENT '反馈内容',
    `quiz_score` DECIMAL(5,3) NULL COMMENT '测验得分（0-1）',
    `self_mastery` DECIMAL(5,3) NULL COMMENT '自评掌握度（0-1）',
    `difficulty_rating` ENUM('too_easy','appropriate','too_hard') NULL COMMENT '难度评价',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`feedback_id`),
    KEY `idx_feedback_profile` (`profile_id`),
    KEY `idx_feedback_resource` (`resource_id`),
    KEY `idx_feedback_course` (`course_id`),
    KEY `idx_feedback_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习反馈表';

-- ============================================================
-- 7. learning_tasks 学习任务表
-- ============================================================
CREATE TABLE IF NOT EXISTS `learning_tasks` (
    `task_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程ID',
    `title` VARCHAR(200) NOT NULL COMMENT '任务标题',
    `description` TEXT NULL COMMENT '任务描述',
    `target_kp_ids` VARCHAR(500) NULL COMMENT '目标知识点ID列表',
    `creator_id` INT UNSIGNED NOT NULL COMMENT '创建人（教师）',
    `assignee_id` INT UNSIGNED NULL COMMENT '指派学生ID',
    `status` ENUM('draft','assigned','in_progress','completed','archived') NOT NULL DEFAULT 'draft' COMMENT '任务状态',
    `due_date` DATETIME NULL COMMENT '截止时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`task_id`),
    KEY `idx_task_course` (`course_id`),
    KEY `idx_task_assignee` (`assignee_id`),
    KEY `idx_task_status` (`status`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习任务表';
