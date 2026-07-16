-- Persist revocable JWT sessions so logout and security-sensitive account changes
-- invalidate access tokens across processes and restarts.

USE `ai_collab_audit_system`;

CREATE TABLE IF NOT EXISTS `auth_sessions` (
    `session_id` CHAR(32) NOT NULL COMMENT 'JWT jti',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `expires_at` DATETIME NOT NULL COMMENT '令牌过期时间',
    `revoked_at` DATETIME NULL COMMENT '撤销时间',
    `revoke_reason` VARCHAR(50) NULL COMMENT '撤销原因',
    `ip_address` VARCHAR(45) NULL COMMENT '登录客户端IP',
    `user_agent` VARCHAR(500) NULL COMMENT '登录客户端User-Agent',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`session_id`),
    KEY `idx_auth_sessions_user_active` (`user_id`, `revoked_at`, `expires_at`),
    KEY `idx_auth_sessions_expiry` (`expires_at`),
    CONSTRAINT `fk_auth_sessions_user`
        FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='可撤销访问令牌会话';
