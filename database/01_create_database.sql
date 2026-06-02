-- ============================================================
-- 01_create_database.sql
-- AI-Collab-Audit-System - 数据库创建脚本
-- Database: ai_collab_audit_system
-- Engine: MySQL 8.0
-- ============================================================

DROP DATABASE IF EXISTS `ai_collab_audit_system`;
CREATE DATABASE `ai_collab_audit_system`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;
USE `ai_collab_audit_system`;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 1;
