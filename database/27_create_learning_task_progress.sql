-- 学习任务按学生隔离的进度记录。
-- 全班任务在 learning_tasks 中只保留发布状态，每名学生的推进状态写入本表。

CREATE TABLE IF NOT EXISTS `learning_task_progress` (
    `progress_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '进度ID',
    `task_id` INT UNSIGNED NOT NULL COMMENT '学习任务ID',
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生用户ID',
    `status` ENUM('assigned','in_progress','completed') NOT NULL DEFAULT 'assigned' COMMENT '学生任务状态',
    `started_at` DATETIME NULL COMMENT '首次开始时间',
    `completed_at` DATETIME NULL COMMENT '完成时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    PRIMARY KEY (`progress_id`),
    UNIQUE KEY `uk_learning_task_student` (`task_id`, `student_id`),
    KEY `idx_learning_task_progress_student` (`student_id`, `status`, `is_deleted`),
    KEY `idx_learning_task_progress_task` (`task_id`, `status`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生学习任务进度表';

-- 个体任务可安全继承旧状态；旧全班任务无法判断由哪名学生推进，因此按未开始回填。
INSERT INTO `learning_task_progress`
    (`task_id`, `student_id`, `status`, `started_at`, `completed_at`, `is_deleted`, `created_at`, `updated_at`)
SELECT
    t.task_id,
    sp.student_id,
    CASE
        WHEN t.assignee_id IS NOT NULL AND t.status IN ('in_progress', 'completed') THEN t.status
        ELSE 'assigned'
    END AS progress_status,
    CASE
        WHEN t.assignee_id IS NOT NULL AND t.status IN ('in_progress', 'completed') THEN COALESCE(t.updated_at, t.created_at)
        ELSE NULL
    END AS started_at,
    CASE
        WHEN t.assignee_id IS NOT NULL AND t.status = 'completed' THEN COALESCE(t.updated_at, t.created_at)
        ELSE NULL
    END AS completed_at,
    0,
    t.created_at,
    COALESCE(t.updated_at, t.created_at)
FROM learning_tasks t
INNER JOIN student_profiles sp
    ON sp.course_id = t.course_id
   AND sp.is_deleted = 0
   AND (t.assignee_id IS NULL OR t.assignee_id = sp.student_id)
INNER JOIN users eligible_student
    ON eligible_student.user_id = sp.student_id
   AND eligible_student.is_deleted = 0
WHERE t.is_deleted = 0
  AND t.status IN ('assigned', 'in_progress', 'completed')
ON DUPLICATE KEY UPDATE `task_id` = VALUES(`task_id`);

-- 历史数据可能包含已删除用户或无对应用户的孤立画像，不计入有效学习进度。
UPDATE learning_task_progress p
LEFT JOIN users u
    ON u.user_id = p.student_id
   AND u.is_deleted = 0
SET p.is_deleted = 1,
    p.updated_at = NOW()
WHERE p.is_deleted = 0
  AND u.user_id IS NULL;
