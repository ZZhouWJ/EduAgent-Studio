-- ============================================================
-- 知识库表扩展：为 course_materials 和 course_material_chunks
-- 添加版本管理、chunk 哈希、embedding 预留字段
-- ============================================================

-- ----------------------------------------------------------
-- 扩展 course_materials 表
-- ----------------------------------------------------------
ALTER TABLE `course_materials`
ADD COLUMN IF NOT EXISTS `material_version` INT NOT NULL DEFAULT 1 COMMENT '资料版本号，每次重解析+1' AFTER `is_deleted`,
ADD COLUMN IF NOT EXISTS `total_chars` INT NULL COMMENT '文档总字符数' AFTER `material_version`,
ADD COLUMN IF NOT EXISTS `last_reparse_at` DATETIME NULL COMMENT '上次重新解析时间' AFTER `total_chars`;

-- ----------------------------------------------------------
-- 扩展 course_material_chunks 表
-- ----------------------------------------------------------
ALTER TABLE `course_material_chunks`
ADD COLUMN IF NOT EXISTS `chunk_hash` VARCHAR(64) NULL COMMENT 'SHA256(content)，用于版本检测和去重' AFTER `is_deleted`,
ADD COLUMN IF NOT EXISTS `material_version` INT NOT NULL DEFAULT 1 COMMENT '所属资料的版本号' AFTER `chunk_hash`,
ADD COLUMN IF NOT EXISTS `embedding_vector_id` INT NULL COMMENT '预留：embedding 向量 ID，接 pgvector 时填充' AFTER `material_version`;

-- ----------------------------------------------------------
-- 为 existing chunks 回填 material_version（默认1）
-- ----------------------------------------------------------
UPDATE `course_material_chunks` SET `material_version` = 1 WHERE `material_version` = 0;

-- ----------------------------------------------------------
-- 为 existing materials 回填 material_version（默认1）
-- ----------------------------------------------------------
UPDATE `course_materials` SET `material_version` = 1 WHERE `material_version` = 0;
