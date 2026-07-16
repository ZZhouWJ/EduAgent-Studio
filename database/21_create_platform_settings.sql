-- Platform-level persistent settings for governance, budgets, and future controls.
USE `ai_collab_audit_system`;

CREATE TABLE IF NOT EXISTS `platform_settings` (
    `setting_key` VARCHAR(100) NOT NULL COMMENT 'Stable setting key',
    `setting_value` JSON NOT NULL COMMENT 'Structured setting value',
    `description` VARCHAR(255) DEFAULT NULL,
    `updated_by` INT UNSIGNED DEFAULT NULL,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`setting_key`),
    KEY `idx_platform_settings_updated_by` (`updated_by`),
    CONSTRAINT `fk_platform_settings_updated_by`
        FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Platform-level persistent settings';

INSERT INTO `platform_settings`
    (`setting_key`, `setting_value`, `description`, `updated_by`)
VALUES
    (
        'governance.rules',
        JSON_OBJECT(
            'fact_consistency_threshold', 80,
            'citation_coverage_threshold', 75,
            'hourly_call_limit', 50,
            'sensitive_content_enabled', TRUE
        ),
        '内容治理阈值、调用限制与敏感内容检测配置',
        NULL
    )
ON DUPLICATE KEY UPDATE `setting_key` = VALUES(`setting_key`);
