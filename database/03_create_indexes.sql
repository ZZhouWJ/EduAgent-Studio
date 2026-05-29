-- ============================================================
-- 03_create_indexes.sql
-- AI-Collab-Audit-System - 补充索引创建脚本
--
-- 说明：
-- 绝大多数索引已在 02_create_tables.sql 的 CREATE TABLE 语句中以内联
-- KEY/INDEX 方式创建。本文件仅包含在 02 中未以内联方式创建的补充索引，
-- 避免 MySQL 报 "Duplicate key name" 错误。
--
-- 当前仅补充 idx_users_username（users 表用户名精确匹配登录查询），
-- 其他索引均已在 02 内联创建。
-- ============================================================

USE `ai_collab_audit_system`;

-- users 表：用户名索引（精确匹配登录查询，未在内联 KEY 中覆盖）
-- 注意：idx_tasks_creator 已在 02_create_tables.sql 的 project_tasks 表内联创建，
-- 此处不再重复创建。
CREATE INDEX idx_users_username ON users(username);
