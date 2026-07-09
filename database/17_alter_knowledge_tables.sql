-- ============================================================
-- 知识库表扩展：为 course_materials 和 course_material_chunks
-- 添加版本管理、chunk 哈希、embedding 预留字段
-- ============================================================

-- ----------------------------------------------------------
-- 扩展 course_materials 表
-- ----------------------------------------------------------
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'course_materials' AND COLUMN_NAME = 'material_version');
SET @sql := IF(@exist > 0, 'SELECT 1', 'ALTER TABLE `course_materials` ADD COLUMN `material_version` INT NOT NULL DEFAULT 1 COMMENT ''资料版本号'' AFTER `is_deleted`');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'course_materials' AND COLUMN_NAME = 'total_chars');
SET @sql := IF(@exist > 0, 'SELECT 1', 'ALTER TABLE `course_materials` ADD COLUMN `total_chars` INT NULL COMMENT ''文档总字符数'' AFTER `material_version`');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'course_materials' AND COLUMN_NAME = 'last_reparse_at');
SET @sql := IF(@exist > 0, 'SELECT 1', 'ALTER TABLE `course_materials` ADD COLUMN `last_reparse_at` DATETIME NULL COMMENT ''上次重新解析时间'' AFTER `total_chars`');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ----------------------------------------------------------
-- 扩展 course_material_chunks 表
-- ----------------------------------------------------------
SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'course_material_chunks' AND COLUMN_NAME = 'chunk_hash');
SET @sql := IF(@exist > 0, 'SELECT 1', 'ALTER TABLE `course_material_chunks` ADD COLUMN `chunk_hash` VARCHAR(64) NULL COMMENT ''SHA256(content)'' AFTER `is_deleted`');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'course_material_chunks' AND COLUMN_NAME = 'material_version');
SET @sql := IF(@exist > 0, 'SELECT 1', 'ALTER TABLE `course_material_chunks` ADD COLUMN `material_version` INT NOT NULL DEFAULT 1 COMMENT ''所属资料版本号'' AFTER `chunk_hash`');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @exist := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'course_material_chunks' AND COLUMN_NAME = 'embedding_vector_id');
SET @sql := IF(@exist > 0, 'SELECT 1', 'ALTER TABLE `course_material_chunks` ADD COLUMN `embedding_vector_id` INT NULL COMMENT ''预留向量ID'' AFTER `material_version`');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ----------------------------------------------------------
-- 为 existing chunks 回填 material_version（默认1）
-- ----------------------------------------------------------
UPDATE `course_material_chunks` SET `material_version` = 1 WHERE `material_version` = 0;

-- ----------------------------------------------------------
-- 为 existing materials 回填 material_version（默认1）
-- ----------------------------------------------------------
UPDATE `course_materials` SET `material_version` = 1 WHERE `material_version` = 0;
