-- Align legacy collaboration roles with the current education product.
USE `ai_collab_audit_system`;

UPDATE `roles`
SET `role_name` = '学生',
    `description` = '使用个性化辅导、学习路径、任务、资源与学习反馈',
    `status` = 'active'
WHERE `role_code` = 'student_member' AND `is_deleted` = 0;

UPDATE `roles`
SET `role_name` = '教师',
    `description` = '管理本人课程、学生画像、学习任务、知识库与 AI 生成资源',
    `status` = 'active'
WHERE `role_code` = 'teacher' AND `is_deleted` = 0;

UPDATE `roles`
SET `role_name` = '系统管理员',
    `description` = '负责平台用户、课程、模型、智能体、审计、成本与内容安全治理',
    `status` = 'active'
WHERE `role_code` = 'admin' AND `is_deleted` = 0;

UPDATE `roles`
SET `role_name` = '历史项目负责人',
    `description` = '旧协作模块兼容角色，当前教育平台不再分配',
    `status` = 'disabled'
WHERE `role_code` = 'project_leader' AND `is_deleted` = 0;
