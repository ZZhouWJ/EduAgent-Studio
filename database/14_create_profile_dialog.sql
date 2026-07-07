-- Profile Dialog Messages: 对话历史
-- 用于存储学生与画像构建助手的对话消息
CREATE TABLE IF NOT EXISTS `profile_dialog_messages` (
  `message_id` INT AUTO_INCREMENT PRIMARY KEY,
  `profile_id` INT NOT NULL COMMENT '关联的画像ID',
  `role` VARCHAR(20) NOT NULL COMMENT 'student/assistant',
  `content` TEXT NOT NULL COMMENT '消息内容',
  `extracted_json` JSON DEFAULT NULL COMMENT '抽取的结构化数据',
  `is_applied` TINYINT DEFAULT 0 COMMENT '是否已应用到画像',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` TINYINT DEFAULT 0,
  INDEX `idx_profile_id` (`profile_id`),
  INDEX `idx_is_applied` (`is_applied`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Profile Update History: 画像更新历史
-- 记录每次画像的变更，便于追溯和回滚
CREATE TABLE IF NOT EXISTS `profile_update_history` (
  `history_id` INT AUTO_INCREMENT PRIMARY KEY,
  `profile_id` INT NOT NULL COMMENT '关联的画像ID',
  `update_type` VARCHAR(50) NOT NULL COMMENT 'dialog/self_report/quiz_result',
  `before_json` JSON NOT NULL COMMENT '更新前的画像数据',
  `after_json` JSON NOT NULL COMMENT '更新后的画像数据',
  `change_summary` VARCHAR(500) COMMENT '变更摘要',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_profile_id` (`profile_id`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
