-- ============================================================
-- 02_create_tables.sql
-- AI-Collab-Audit-System - 数据表创建脚本
-- 共 27 张表，严格按照 Schema 冻结说明创建
-- ============================================================

USE `ai_collab_audit_system`;

-- ============================================================
-- 1. users 用户表
-- ============================================================
CREATE TABLE `users` (
    `user_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名（登录名）',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    `real_name` VARCHAR(100) NOT NULL COMMENT '真实姓名',
    `student_no` VARCHAR(30) NULL COMMENT '学号（学生用户填写）',
    `email` VARCHAR(255) NULL COMMENT '邮箱',
    `phone` VARCHAR(20) NULL COMMENT '手机号',
    `status` ENUM('active','disabled') NOT NULL DEFAULT 'active' COMMENT '账号状态：active=正常，disabled=禁用',
    `last_login_at` DATETIME NULL COMMENT '最后登录时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `uk_users_username` (`username`),
    UNIQUE KEY `uk_users_student_no` (`student_no`),
    UNIQUE KEY `uk_users_email` (`email`),
    KEY `idx_users_status_deleted` (`status`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================================
-- 2. roles 角色表
-- ============================================================
CREATE TABLE `roles` (
    `role_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '角色ID',
    `role_name` VARCHAR(50) NOT NULL COMMENT '角色名称',
    `role_code` VARCHAR(50) NOT NULL COMMENT '角色代码（唯一标识）',
    `description` VARCHAR(255) NULL COMMENT '角色描述',
    `status` ENUM('active','disabled') NOT NULL DEFAULT 'active' COMMENT '状态：active=正常，disabled=禁用',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`role_id`),
    UNIQUE KEY `uk_roles_role_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- ============================================================
-- 3. user_roles 用户角色关联表
-- ============================================================
CREATE TABLE `user_roles` (
    `user_role_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户角色关联ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `role_id` INT UNSIGNED NOT NULL COMMENT '角色ID',
    `assigned_by` INT UNSIGNED NULL COMMENT '分配人',
    `assigned_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '分配时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`user_role_id`),
    UNIQUE KEY `uk_user_roles_user_role` (`user_id`, `role_id`, `is_deleted`),
    KEY `idx_user_roles_role` (`role_id`),
    CONSTRAINT `fk_user_roles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `fk_user_roles_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- ============================================================
-- 4. permissions 权限表
-- ============================================================
CREATE TABLE `permissions` (
    `permission_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '权限ID',
    `permission_name` VARCHAR(100) NOT NULL COMMENT '权限名称',
    `permission_code` VARCHAR(100) NOT NULL COMMENT '权限代码（唯一标识）',
    `module_name` VARCHAR(50) NOT NULL COMMENT '所属模块',
    `description` VARCHAR(255) NULL COMMENT '权限描述',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`permission_id`),
    UNIQUE KEY `uk_permissions_code` (`permission_code`),
    KEY `idx_permissions_module` (`module_name`, `is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- ============================================================
-- 5. role_permissions 角色权限关联表
-- ============================================================
CREATE TABLE `role_permissions` (
    `role_permission_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '角色权限关联ID',
    `role_id` INT UNSIGNED NOT NULL COMMENT '角色ID',
    `permission_id` INT UNSIGNED NOT NULL COMMENT '权限ID',
    `assigned_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '分配时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`role_permission_id`),
    UNIQUE KEY `uk_role_permissions_pair` (`role_id`, `permission_id`, `is_deleted`),
    KEY `idx_role_permissions_permission` (`permission_id`),
    CONSTRAINT `fk_role_permissions_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`),
    CONSTRAINT `fk_role_permissions_permission` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- ============================================================
-- 6. projects 项目空间表
-- ============================================================
CREATE TABLE `projects` (
    `project_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '项目ID',
    `project_name` VARCHAR(200) NOT NULL COMMENT '项目名称',
    `project_type` VARCHAR(50) NULL COMMENT '项目类型',
    `description` TEXT NULL COMMENT '项目描述',
    `owner_id` INT UNSIGNED NOT NULL COMMENT '项目负责人用户ID',
    `status` ENUM('active','archived','suspended') NOT NULL DEFAULT 'active' COMMENT '项目状态：active=进行中，archived=已归档，suspended=已暂停',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`project_id`),
    KEY `idx_projects_owner` (`owner_id`),
    KEY `idx_projects_status_deleted` (`status`, `is_deleted`),
    CONSTRAINT `fk_projects_owner` FOREIGN KEY (`owner_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目空间表';

-- ============================================================
-- 7. project_members 项目成员表
-- project_role 枚举值：member/leader/reviewer/teacher
-- ============================================================
CREATE TABLE `project_members` (
    `member_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '成员ID',
    `project_id` INT UNSIGNED NOT NULL COMMENT '项目ID',
    `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
    `project_role` ENUM('member','leader','reviewer','teacher') NOT NULL DEFAULT 'member' COMMENT '项目内角色：member=普通成员，leader=项目负责人，reviewer=质量审核员，teacher=指导教师',
    `joined_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    `status` ENUM('active','inactive') NOT NULL DEFAULT 'active' COMMENT '成员状态：active=活跃，inactive=不活跃',
    `contribution_score` DECIMAL(5,2) NULL COMMENT '贡献评分（0-100）',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`member_id`),
    UNIQUE KEY `uk_project_members_unique` (`project_id`, `user_id`, `is_deleted`),
    KEY `idx_project_members_project` (`project_id`, `is_deleted`),
    KEY `idx_project_members_user` (`user_id`, `is_deleted`),
    CONSTRAINT `fk_project_members_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
    CONSTRAINT `fk_project_members_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目成员表';

-- ============================================================
-- 8. task_types 任务类型表
-- ============================================================
CREATE TABLE `task_types` (
    `task_type_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务类型ID',
    `type_name` VARCHAR(100) NOT NULL COMMENT '类型名称',
    `type_code` VARCHAR(50) NOT NULL COMMENT '类型代码（唯一标识）',
    `description` VARCHAR(255) NULL COMMENT '类型描述',
    `default_template_id` INT UNSIGNED NULL COMMENT '默认关联的提示词模板ID',
    `status` ENUM('active','disabled') NOT NULL DEFAULT 'active' COMMENT '状态：active=可用，disabled=不可用',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`task_type_id`),
    UNIQUE KEY `uk_task_types_code` (`type_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务类型表';

-- ============================================================
-- 9. project_tasks 项目任务表
-- ============================================================
CREATE TABLE `project_tasks` (
    `task_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
    `project_id` INT UNSIGNED NOT NULL COMMENT '项目ID',
    `task_type_id` INT UNSIGNED NOT NULL COMMENT '任务类型ID',
    `title` VARCHAR(200) NOT NULL COMMENT '任务标题',
    `description` TEXT NULL COMMENT '任务描述',
    `creator_id` INT UNSIGNED NOT NULL COMMENT '任务创建人',
    `assignee_id` INT UNSIGNED NULL COMMENT '任务负责人',
    `status` ENUM('draft','running','generated','submitted','approved','rejected','revision_required','adopted','archived','conflict_pending') NOT NULL DEFAULT 'draft' COMMENT '任务状态：draft=草稿，running=进行中，generated=已生成，submitted=已提交，approved=已通过，rejected=已拒绝，revision_required=需修改，adopted=已采用，archived=已归档，conflict_pending=冲突待处理',
    `priority` ENUM('low','normal','high','urgent') NOT NULL DEFAULT 'normal' COMMENT '优先级：low=低，normal=普通，high=高，urgent=紧急',
    `due_date` DATETIME NULL COMMENT '截止时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`task_id`),
    KEY `idx_tasks_project_status` (`project_id`, `status`, `is_deleted`),
    KEY `idx_tasks_assignee` (`assignee_id`, `is_deleted`),
    KEY `idx_tasks_creator` (`creator_id`),
    CONSTRAINT `fk_tasks_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
    CONSTRAINT `fk_tasks_task_type` FOREIGN KEY (`task_type_id`) REFERENCES `task_types` (`task_type_id`),
    CONSTRAINT `fk_tasks_creator` FOREIGN KEY (`creator_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `fk_tasks_assignee` FOREIGN KEY (`assignee_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目任务表';

-- ============================================================
-- 10. prompt_templates 提示词模板表
-- ============================================================
CREATE TABLE `prompt_templates` (
    `template_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '模板ID',
    `template_name` VARCHAR(200) NOT NULL COMMENT '模板名称',
    `task_type_id` INT UNSIGNED NOT NULL COMMENT '关联的任务类型ID',
    `description` VARCHAR(500) NULL COMMENT '模板描述',
    `current_version_id` INT UNSIGNED NULL COMMENT '当前启用的版本ID',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用：1=启用，0=禁用',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`template_id`),
    KEY `idx_prompt_templates_task_type` (`task_type_id`, `is_deleted`),
    CONSTRAINT `fk_prompt_templates_task_type` FOREIGN KEY (`task_type_id`) REFERENCES `task_types` (`task_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提示词模板表';

-- ============================================================
-- 11. prompt_versions 提示词版本表
-- ============================================================
CREATE TABLE `prompt_versions` (
    `prompt_version_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '提示词版本ID',
    `template_id` INT UNSIGNED NOT NULL COMMENT '所属模板ID',
    `version_no` INT UNSIGNED NOT NULL COMMENT '版本号',
    `prompt_content` TEXT NOT NULL COMMENT '提示词内容',
    `change_note` VARCHAR(500) NULL COMMENT '变更说明',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`prompt_version_id`),
    UNIQUE KEY `uk_prompt_versions_template_version` (`template_id`, `version_no`),
    KEY `idx_prompt_versions_template` (`template_id`),
    CONSTRAINT `fk_prompt_versions_template` FOREIGN KEY (`template_id`) REFERENCES `prompt_templates` (`template_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提示词版本表';

-- ============================================================
-- 12. model_providers 模型供应商表
-- ============================================================
CREATE TABLE `model_providers` (
    `provider_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '供应商ID',
    `provider_name` VARCHAR(100) NOT NULL COMMENT '供应商名称',
    `provider_code` VARCHAR(50) NOT NULL COMMENT '供应商代码（唯一标识）',
    `base_url` VARCHAR(500) NULL COMMENT 'API base URL',
    `website` VARCHAR(255) NULL COMMENT '官网地址',
    `description` VARCHAR(500) NULL COMMENT '供应商描述',
    `status` ENUM('active','disabled') NOT NULL DEFAULT 'active' COMMENT '状态：active=正常，disabled=停用',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`provider_id`),
    UNIQUE KEY `uk_model_providers_code` (`provider_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模型供应商表';

-- ============================================================
-- 13. ai_models AI模型表
-- ============================================================
CREATE TABLE `ai_models` (
    `model_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '模型ID',
    `provider_id` INT UNSIGNED NOT NULL COMMENT '所属供应商ID',
    `model_name` VARCHAR(100) NOT NULL COMMENT '模型内部名称',
    `display_name` VARCHAR(100) NOT NULL COMMENT '展示名称',
    `capability_tags` VARCHAR(500) NULL COMMENT '能力标签，逗号分隔',
    `max_context` INT UNSIGNED NULL COMMENT '最大上下文 token 数',
    `input_price` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '输入价格（每 price_unit 的价格）',
    `output_price` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '输出价格（每 price_unit 的价格）',
    `price_unit` VARCHAR(20) NOT NULL DEFAULT '1K_TOKENS' COMMENT '价格单位（默认 1K_TOKENS）',
    `status` ENUM('active','disabled') NOT NULL DEFAULT 'active' COMMENT '状态：active=可用，disabled=停用',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`model_id`),
    UNIQUE KEY `uk_ai_models_provider_name` (`provider_id`, `model_name`, `is_deleted`),
    KEY `idx_ai_models_status` (`status`, `is_deleted`),
    CONSTRAINT `fk_ai_models_provider` FOREIGN KEY (`provider_id`) REFERENCES `model_providers` (`provider_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI模型表';

-- ============================================================
-- 14. api_configs API配置表
-- ============================================================
CREATE TABLE `api_configs` (
    `api_config_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'API配置ID',
    `provider_id` INT UNSIGNED NOT NULL COMMENT '所属供应商ID',
    `config_name` VARCHAR(100) NOT NULL COMMENT '配置名称',
    `encrypted_api_key` TEXT NOT NULL COMMENT 'AES-256-GCM 加密后的 API Key',
    `key_iv` VARCHAR(64) NOT NULL COMMENT 'AES-256-GCM 加密 IV（Base64）',
    `key_tag` VARCHAR(64) NOT NULL COMMENT 'AES-256-GCM 认证标签（Base64）',
    `key_version` INT NOT NULL DEFAULT 1 COMMENT '密钥版本号',
    `key_mask` VARCHAR(50) NOT NULL COMMENT 'API Key 脱敏值，例如 sk-****abcd',
    `quota_limit` DECIMAL(15,2) NULL COMMENT '额度上限',
    `used_quota` DECIMAL(15,2) NOT NULL DEFAULT 0 COMMENT '已使用额度',
    `status` ENUM('active','disabled') NOT NULL DEFAULT 'active' COMMENT '状态：active=正常，disabled=停用',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`api_config_id`),
    KEY `idx_api_configs_provider` (`provider_id`, `is_deleted`),
    CONSTRAINT `fk_api_configs_provider` FOREIGN KEY (`provider_id`) REFERENCES `model_providers` (`provider_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API配置表';

-- ============================================================
-- 15. task_branches 任务分支表
-- ============================================================
CREATE TABLE `task_branches` (
    `branch_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分支ID',
    `project_id` INT UNSIGNED NOT NULL COMMENT '项目ID',
    `task_id` INT UNSIGNED NOT NULL COMMENT '任务ID',
    `branch_name` VARCHAR(200) NOT NULL COMMENT '分支名称',
    `base_output_id` INT UNSIGNED NULL COMMENT '基准输出版本ID（待 task_outputs 创建后通过 ALTER TABLE 添加外键）',
    `status` ENUM('active','merged','closed','conflict_pending') NOT NULL DEFAULT 'active' COMMENT '分支状态：active=活跃，merged=已合并，closed=已关闭，conflict_pending=冲突待处理',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`branch_id`),
    KEY `idx_task_branches_task` (`task_id`, `is_deleted`),
    KEY `idx_task_branches_project` (`project_id`),
    KEY `idx_task_branches_status` (`status`),
    CONSTRAINT `fk_task_branches_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
    CONSTRAINT `fk_task_branches_task` FOREIGN KEY (`task_id`) REFERENCES `project_tasks` (`task_id`)
    -- fk_task_branches_base_output 在所有表创建后通过 ALTER TABLE 添加（避免循环依赖）
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务分支表';

-- ============================================================
-- 16. ai_invocations AI调用记录表（审计表，不做业务删除）
-- ============================================================
CREATE TABLE `ai_invocations` (
    `invocation_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '调用记录ID',
    `project_id` INT UNSIGNED NULL COMMENT '项目ID',
    `task_id` INT UNSIGNED NULL COMMENT '任务ID',
    `branch_id` INT UNSIGNED NULL COMMENT '分支ID',
    `model_id` INT UNSIGNED NULL COMMENT '模型ID',
    `prompt_version_id` INT UNSIGNED NULL COMMENT '提示词版本ID',
    `input_text` LONGTEXT NOT NULL COMMENT '输入文本',
    `output_text` LONGTEXT NULL COMMENT '输出文本',
    `input_tokens` INT UNSIGNED NULL COMMENT '输入 token 数',
    `output_tokens` INT UNSIGNED NULL COMMENT '输出 token 数',
    `latency_ms` INT UNSIGNED NULL COMMENT '延迟（毫秒）',
    `status` ENUM('success','failed','timeout','blocked') NOT NULL DEFAULT 'success' COMMENT '调用状态：success=成功，failed=失败，timeout=超时，blocked=阻断',
    `error_message` TEXT NULL COMMENT '错误信息',
    `created_by` INT UNSIGNED NULL COMMENT '调用发起人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '调用时间',
    PRIMARY KEY (`invocation_id`),
    KEY `idx_ai_invocations_task` (`task_id`),
    KEY `idx_ai_invocations_model` (`model_id`),
    KEY `idx_ai_invocations_created_at` (`created_at`),
    KEY `idx_ai_invocations_project` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI调用记录表（审计表，不做物理删除）';

-- ============================================================
-- 17. task_outputs 任务输出版本表
-- status 枚举值：draft/generated/submitted/approved/rejected/revision_required/adopted/conflict_pending
-- ============================================================
CREATE TABLE `task_outputs` (
    `output_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '输出版本ID',
    `task_id` INT UNSIGNED NOT NULL COMMENT '任务ID',
    `branch_id` INT UNSIGNED NULL COMMENT '所属分支ID',
    `invocation_id` BIGINT UNSIGNED NULL COMMENT '关联的AI调用记录ID',
    `version_no` INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '版本号',
    `output_title` VARCHAR(200) NOT NULL COMMENT '输出标题',
    `content` LONGTEXT NOT NULL COMMENT '输出内容',
    `source_type` ENUM('ai_generated','manual_edit','hybrid','manual_merge') NOT NULL COMMENT '内容来源：ai_generated=AI生成，manual_edit=人工编辑，hybrid=混合，manual_merge=手动合并',
    `parent_output_id` INT UNSIGNED NULL COMMENT '父版本ID（用于版本链路追溯）',
    `lock_version` INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '乐观锁版本号',
    `last_modified_at` DATETIME NULL COMMENT '最后修改时间',
    `last_modified_by` INT UNSIGNED NULL COMMENT '最后修改人',
    `edit_summary` VARCHAR(500) NULL COMMENT '本次编辑说明',
    `is_final_candidate` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否候选最终版本：1=是，0=否',
    `status` ENUM('draft','generated','submitted','approved','rejected','revision_required','adopted','conflict_pending') NOT NULL DEFAULT 'draft' COMMENT '输出状态：draft=草稿，generated=已生成，submitted=已提交，approved=已通过，rejected=已拒绝，revision_required=需修改，adopted=已采用，conflict_pending=冲突待处理',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`output_id`),
    KEY `idx_task_outputs_task` (`task_id`, `is_deleted`),
    KEY `idx_task_outputs_parent` (`parent_output_id`),
    KEY `idx_task_outputs_branch` (`branch_id`),
    KEY `idx_task_outputs_status` (`status`, `is_deleted`),
    KEY `idx_task_outputs_invocation` (`invocation_id`),
    CONSTRAINT `fk_task_outputs_task` FOREIGN KEY (`task_id`) REFERENCES `project_tasks` (`task_id`),
    CONSTRAINT `fk_task_outputs_branch` FOREIGN KEY (`branch_id`) REFERENCES `task_branches` (`branch_id`),
    CONSTRAINT `fk_task_outputs_invocation` FOREIGN KEY (`invocation_id`) REFERENCES `ai_invocations` (`invocation_id`),
    CONSTRAINT `fk_task_outputs_parent` FOREIGN KEY (`parent_output_id`) REFERENCES `task_outputs` (`output_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务输出版本表';

-- ============================================================
-- 18. review_requests 审核请求表
-- ============================================================
CREATE TABLE `review_requests` (
    `request_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '审核请求ID',
    `output_id` INT UNSIGNED NOT NULL COMMENT '待审核的输出版本ID',
    `task_id` INT UNSIGNED NOT NULL COMMENT '关联任务ID',
    `project_id` INT UNSIGNED NOT NULL COMMENT '关联项目ID',
    `submitter_id` INT UNSIGNED NOT NULL COMMENT '提交人',
    `reviewer_id` INT UNSIGNED NULL COMMENT '指定审核人',
    `request_status` ENUM('pending','approved','rejected','revision_required') NOT NULL DEFAULT 'pending' COMMENT '审核状态：pending=待审核，approved=通过，rejected=拒绝，revision_required=需修改',
    `submit_note` TEXT NULL COMMENT '提交说明',
    `reviewed_at` DATETIME NULL COMMENT '审核时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`request_id`),
    KEY `idx_review_requests_output` (`output_id`),
    KEY `idx_review_requests_status` (`request_status`, `is_deleted`),
    KEY `idx_review_requests_project` (`project_id`),
    KEY `idx_review_requests_reviewer` (`reviewer_id`),
    CONSTRAINT `fk_review_requests_output` FOREIGN KEY (`output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_review_requests_task` FOREIGN KEY (`task_id`) REFERENCES `project_tasks` (`task_id`),
    CONSTRAINT `fk_review_requests_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
    CONSTRAINT `fk_review_requests_submitter` FOREIGN KEY (`submitter_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `fk_review_requests_reviewer` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审核请求表';

-- ============================================================
-- 19. output_reviews 输出审核表
-- ============================================================
CREATE TABLE `output_reviews` (
    `review_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '审核记录ID',
    `request_id` INT UNSIGNED NOT NULL COMMENT '审核请求ID',
    `output_id` INT UNSIGNED NOT NULL COMMENT '输出版本ID',
    `reviewer_id` INT UNSIGNED NOT NULL COMMENT '审核人',
    `accuracy_score` DECIMAL(3,1) NULL COMMENT '准确性评分（0-10）',
    `completeness_score` DECIMAL(3,1) NULL COMMENT '完整性评分（0-10）',
    `logic_score` DECIMAL(3,1) NULL COMMENT '逻辑性评分（0-10）',
    `format_score` DECIMAL(3,1) NULL COMMENT '规范性评分（0-10）',
    `usability_score` DECIMAL(3,1) NULL COMMENT '可用性评分（0-10）',
    `risk_score` DECIMAL(3,1) NULL COMMENT '风险评分（0-10，越高风险越大）',
    `review_status` ENUM('pending','approved','rejected','revision_required') NOT NULL COMMENT '审核结论：pending=待审，approved=通过，rejected=拒绝，revision_required=需修改',
    `review_comment` TEXT NULL COMMENT '审核意见',
    `reviewed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '审核时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`review_id`),
    KEY `idx_output_reviews_output` (`output_id`),
    KEY `idx_output_reviews_request` (`request_id`),
    KEY `idx_output_reviews_reviewer` (`reviewer_id`),
    CONSTRAINT `fk_output_reviews_request` FOREIGN KEY (`request_id`) REFERENCES `review_requests` (`request_id`),
    CONSTRAINT `fk_output_reviews_output` FOREIGN KEY (`output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_output_reviews_reviewer` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='输出审核表';

-- ============================================================
-- 20. issue_tags 问题标签表
-- severity 枚举值：low/medium/high
-- ============================================================
CREATE TABLE `issue_tags` (
    `tag_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '标签ID',
    `tag_name` VARCHAR(50) NOT NULL COMMENT '标签名称',
    `tag_code` VARCHAR(50) NOT NULL COMMENT '标签代码（唯一标识）',
    `description` VARCHAR(255) NULL COMMENT '标签描述',
    `severity` ENUM('low','medium','high') NOT NULL DEFAULT 'low' COMMENT '严重程度：low=轻微，medium=中等，high=严重',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`tag_id`),
    UNIQUE KEY `uk_issue_tags_code` (`tag_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问题标签表';

-- ============================================================
-- 21. output_issue_relations 输出问题关联表
-- ============================================================
CREATE TABLE `output_issue_relations` (
    `relation_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '关联ID',
    `output_id` INT UNSIGNED NOT NULL COMMENT '输出版本ID',
    `review_id` INT UNSIGNED NULL COMMENT '关联审核ID（可为空）',
    `tag_id` INT UNSIGNED NOT NULL COMMENT '问题标签ID',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`relation_id`),
    KEY `idx_output_issue_relations_output` (`output_id`),
    KEY `idx_output_issue_relations_review` (`review_id`),
    KEY `idx_output_issue_relations_tag` (`tag_id`),
    CONSTRAINT `fk_output_issue_relations_output` FOREIGN KEY (`output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_output_issue_relations_review` FOREIGN KEY (`review_id`) REFERENCES `output_reviews` (`review_id`),
    CONSTRAINT `fk_output_issue_relations_tag` FOREIGN KEY (`tag_id`) REFERENCES `issue_tags` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='输出问题关联表';

-- ============================================================
-- 22. output_comments 输出批注表
-- status 枚举值：open/resolved/closed
-- ============================================================
CREATE TABLE `output_comments` (
    `comment_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '批注ID',
    `output_id` INT UNSIGNED NOT NULL COMMENT '输出版本ID',
    `commenter_id` INT UNSIGNED NOT NULL COMMENT '批注人',
    `comment_type` ENUM('comment','suggestion','approval') NOT NULL DEFAULT 'comment' COMMENT '批注类型：comment=普通批注，suggestion=建议，approval=批准',
    `comment_text` TEXT NOT NULL COMMENT '批注内容',
    `status` ENUM('open','resolved','closed') NOT NULL DEFAULT 'open' COMMENT '批注状态：open=待处理，resolved=已处理，closed=已关闭',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`comment_id`),
    KEY `idx_output_comments_output` (`output_id`, `is_deleted`),
    KEY `idx_output_comments_commenter` (`commenter_id`),
    CONSTRAINT `fk_output_comments_output` FOREIGN KEY (`output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_output_comments_commenter` FOREIGN KEY (`commenter_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='输出批注表';

-- ============================================================
-- 23. adopted_outputs 采用成果表
-- ============================================================
CREATE TABLE `adopted_outputs` (
    `adopted_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '采用成果ID',
    `project_id` INT UNSIGNED NOT NULL COMMENT '项目ID',
    `task_id` INT UNSIGNED NOT NULL COMMENT '任务ID',
    `output_id` INT UNSIGNED NOT NULL COMMENT '输出版本ID',
    `artifact_title` VARCHAR(200) NOT NULL COMMENT '成果标题',
    `artifact_type` VARCHAR(50) NULL COMMENT '成果类型',
    `release_version` VARCHAR(50) NULL COMMENT '发布版本号',
    `adopted_by` INT UNSIGNED NOT NULL COMMENT '采用操作人',
    `adopted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '采用时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`adopted_id`),
    KEY `idx_adopted_outputs_project` (`project_id`, `is_deleted`),
    KEY `idx_adopted_outputs_task` (`task_id`),
    KEY `idx_adopted_outputs_output` (`output_id`),
    CONSTRAINT `fk_adopted_outputs_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
    CONSTRAINT `fk_adopted_outputs_task` FOREIGN KEY (`task_id`) REFERENCES `project_tasks` (`task_id`),
    CONSTRAINT `fk_adopted_outputs_output` FOREIGN KEY (`output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_adopted_outputs_user` FOREIGN KEY (`adopted_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采用成果表';

-- ============================================================
-- 24. merge_records 分支合并记录表
-- merge_strategy 枚举值：adopt_source/adopt_target/manual_merge/adopt_separately
-- ============================================================
CREATE TABLE `merge_records` (
    `merge_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '合并记录ID',
    `project_id` INT UNSIGNED NOT NULL COMMENT '项目ID',
    `task_id` INT UNSIGNED NOT NULL COMMENT '任务ID',
    `base_output_id` INT UNSIGNED NULL COMMENT '基准输出版本ID',
    `source_output_id` INT UNSIGNED NULL COMMENT '源输出版本ID',
    `target_output_id` INT UNSIGNED NULL COMMENT '目标输出版本ID',
    `merged_output_id` INT UNSIGNED NULL COMMENT '合并后生成的新版本ID',
    `merge_strategy` ENUM('adopt_source','adopt_target','manual_merge','adopt_separately') NOT NULL DEFAULT 'manual_merge' COMMENT '合并策略：adopt_source=采用来源版本，adopt_target=采用目标版本，manual_merge=手动合并生成新版本，adopt_separately=分别作为独立成果采用',
    `merge_comment` VARCHAR(500) NULL COMMENT '合并说明',
    `merged_by` INT UNSIGNED NOT NULL COMMENT '合并操作人',
    `merged_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '合并时间',
    `is_deleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '软删除标记：0=未删除，1=已删除',
    `deleted_at` DATETIME NULL COMMENT '删除时间',
    `deleted_by` INT UNSIGNED NULL COMMENT '删除操作人',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `created_by` INT UNSIGNED NULL COMMENT '创建人',
    `updated_at` DATETIME NULL COMMENT '更新时间',
    `updated_by` INT UNSIGNED NULL COMMENT '更新人',
    PRIMARY KEY (`merge_id`),
    KEY `idx_merge_records_task` (`task_id`),
    KEY `idx_merge_records_project` (`project_id`),
    KEY `idx_merge_records_merged_by` (`merged_by`),
    CONSTRAINT `fk_merge_records_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`project_id`),
    CONSTRAINT `fk_merge_records_task` FOREIGN KEY (`task_id`) REFERENCES `project_tasks` (`task_id`),
    CONSTRAINT `fk_merge_records_base_output` FOREIGN KEY (`base_output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_merge_records_source_output` FOREIGN KEY (`source_output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_merge_records_target_output` FOREIGN KEY (`target_output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_merge_records_merged_output` FOREIGN KEY (`merged_output_id`) REFERENCES `task_outputs` (`output_id`),
    CONSTRAINT `fk_merge_records_merged_by` FOREIGN KEY (`merged_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分支合并记录表';

-- ============================================================
-- 25. cost_records 成本记录表（审计表，不做业务删除）
-- ============================================================
CREATE TABLE `cost_records` (
    `cost_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '成本记录ID',
    `invocation_id` BIGINT UNSIGNED NOT NULL COMMENT 'AI调用记录ID',
    `project_id` INT UNSIGNED NULL COMMENT '项目ID',
    `task_id` INT UNSIGNED NULL COMMENT '任务ID',
    `model_id` INT UNSIGNED NULL COMMENT '模型ID',
    `user_id` INT UNSIGNED NULL COMMENT '操作用户ID',
    `input_tokens` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '输入token数',
    `output_tokens` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '输出token数',
    `total_tokens` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '总token数',
    `input_cost` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '输入成本',
    `output_cost` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '输出成本',
    `total_cost` DECIMAL(10,6) NOT NULL DEFAULT 0 COMMENT '总成本',
    `currency` VARCHAR(10) NOT NULL DEFAULT 'CNY' COMMENT '货币单位',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    PRIMARY KEY (`cost_id`),
    KEY `idx_cost_records_invocation` (`invocation_id`),
    KEY `idx_cost_records_project` (`project_id`),
    KEY `idx_cost_records_model` (`model_id`),
    KEY `idx_cost_records_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成本记录表（审计/统计表，不做物理删除）';

-- ============================================================
-- 26. operation_logs 操作日志表（审计表，不做物理删除）
-- ============================================================
CREATE TABLE `operation_logs` (
    `log_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    `user_id` INT UNSIGNED NULL COMMENT '操作用户ID',
    `project_id` INT UNSIGNED NULL COMMENT '关联项目ID',
    `task_id` INT UNSIGNED NULL COMMENT '关联任务ID',
    `target_type` VARCHAR(50) NULL COMMENT '操作对象类型（表名）',
    `target_id` BIGINT UNSIGNED NULL COMMENT '操作对象ID',
    `action_type` VARCHAR(50) NOT NULL COMMENT '操作类型（create/update/delete/submit/review/adopt/merge/archive 等）',
    `action_desc` VARCHAR(500) NOT NULL COMMENT '操作描述',
    `old_value` TEXT NULL COMMENT '变更前值（JSON）',
    `new_value` TEXT NULL COMMENT '变更后值（JSON）',
    `ip_address` VARCHAR(45) NULL COMMENT '客户端IP',
    `user_agent` VARCHAR(500) NULL COMMENT 'User-Agent',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    PRIMARY KEY (`log_id`),
    KEY `idx_operation_logs_user_time` (`user_id`, `created_at`),
    KEY `idx_operation_logs_project` (`project_id`),
    KEY `idx_operation_logs_task` (`task_id`),
    KEY `idx_operation_logs_target` (`target_type`, `target_id`),
    KEY `idx_operation_logs_action_type` (`action_type`),
    KEY `idx_operation_logs_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表（审计表，不做物理删除）';

-- ============================================================
-- 27. login_logs 登录日志表（审计表，不做物理删除）
-- ============================================================
CREATE TABLE `login_logs` (
    `login_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '登录日志ID',
    `user_id` INT UNSIGNED NULL COMMENT '用户ID（登录成功时填写）',
    `username` VARCHAR(50) NOT NULL COMMENT '登录尝试的用户名',
    `login_status` ENUM('success','failed') NOT NULL COMMENT '登录状态：success=成功，failed=失败',
    `failure_reason` VARCHAR(100) NULL COMMENT '失败原因',
    `ip_address` VARCHAR(45) NULL COMMENT '客户端IP',
    `user_agent` VARCHAR(500) NULL COMMENT 'User-Agent',
    `login_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    PRIMARY KEY (`login_id`),
    KEY `idx_login_logs_user_time` (`user_id`, `login_time`),
    KEY `idx_login_logs_username_time` (`username`, `login_time`),
    KEY `idx_login_logs_login_time` (`login_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录日志表（审计表，不做物理删除）';

-- ============================================================
-- 附录：解决 task_branches 与 task_outputs 的循环外键依赖
-- task_branches.base_output_id 引用 task_outputs.output_id
-- task_outputs.branch_id        引用 task_branches.branch_id
-- 两表相互引用，在各自的 CREATE TABLE 内无法同时满足
-- 因此在所有 27 张表创建完成后，通过 ALTER TABLE 添加缺失的外键约束
-- ============================================================

ALTER TABLE `task_branches`
    ADD CONSTRAINT `fk_task_branches_base_output`
    FOREIGN KEY (`base_output_id`) REFERENCES `task_outputs` (`output_id`);
