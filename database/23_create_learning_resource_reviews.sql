-- Persist the complete submit-review-publish history for generated learning resources.
USE `ai_collab_audit_system`;

CREATE TABLE IF NOT EXISTS `learning_resource_reviews` (
    `review_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '资源审核记录ID',
    `resource_id` INT UNSIGNED NOT NULL COMMENT '学习资源ID',
    `submitter_id` INT UNSIGNED NOT NULL COMMENT '送审人',
    `reviewer_id` INT UNSIGNED NULL COMMENT '审核人',
    `review_status` ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    `submit_note` VARCHAR(500) NULL COMMENT '送审说明',
    `accuracy_score` DECIMAL(3,1) NULL COMMENT '内容准确性（0-10）',
    `completeness_score` DECIMAL(3,1) NULL COMMENT '内容完整性（0-10）',
    `logic_score` DECIMAL(3,1) NULL COMMENT '逻辑严谨性（0-10）',
    `format_score` DECIMAL(3,1) NULL COMMENT '格式规范性（0-10）',
    `usability_score` DECIMAL(3,1) NULL COMMENT '教学可用性（0-10）',
    `review_comment` TEXT NULL COMMENT '审核意见',
    `submitted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '送审时间',
    `reviewed_at` DATETIME NULL COMMENT '审核时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL,
    PRIMARY KEY (`review_id`),
    KEY `idx_resource_reviews_resource` (`resource_id`, `is_deleted`, `review_id`),
    KEY `idx_resource_reviews_status` (`review_status`, `is_deleted`, `submitted_at`),
    KEY `idx_resource_reviews_submitter` (`submitter_id`),
    KEY `idx_resource_reviews_reviewer` (`reviewer_id`),
    CONSTRAINT `fk_resource_reviews_resource`
        FOREIGN KEY (`resource_id`) REFERENCES `learning_resources` (`resource_id`),
    CONSTRAINT `fk_resource_reviews_submitter`
        FOREIGN KEY (`submitter_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `fk_resource_reviews_reviewer`
        FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`user_id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='学习资源送审与审核历史';
