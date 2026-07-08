-- ============================================================
-- 证据链路相关表：kp_chunk_links + resource_evidence_links
-- ============================================================

-- ----------------------------------------------------------
-- 表1：kp_chunk_links（知识点-Chunk 多对多关联）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS `kp_chunk_links` (
    `link_id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `chunk_id` INT UNSIGNED NOT NULL COMMENT '关联的 chunk ID',
    `kp_id` INT UNSIGNED NOT NULL COMMENT '关联的知识点 ID',
    `match_method` ENUM('bm25', 'embedding', 'llm_verify', 'manual') NOT NULL DEFAULT 'bm25' COMMENT '匹配方法',
    `relevance_score` DECIMAL(5,4) NOT NULL COMMENT '相关度评分 0.0000~1.0000',
    `status` ENUM('pending', 'confirmed', 'rejected') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    `verified_by` INT UNSIGNED NULL COMMENT '审核教师用户 ID',
    `verified_at` DATETIME NULL COMMENT '审核时间',
    `match_version` INT NOT NULL DEFAULT 1 COMMENT '匹配版本号，用于重匹配追踪',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX `idx_chunk_id` (`chunk_id`),
    INDEX `idx_kp_id` (`kp_id`),
    INDEX `idx_status` (`status`),
    UNIQUE KEY `uk_chunk_kp` (`chunk_id`, `kp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点与 Chunk 多对多关联表';

-- ----------------------------------------------------------
-- 表2：resource_evidence_links（资源-证据关联）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS `resource_evidence_links` (
    `link_id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `resource_id` INT UNSIGNED NOT NULL COMMENT '关联的资源 ID',
    `chunk_id` INT UNSIGNED NOT NULL COMMENT '引用的 chunk ID',
    `kp_id` INT UNSIGNED NOT NULL COMMENT '关联的知识点 ID',
    `quote_text` TEXT NOT NULL COMMENT '资源中引用的原文片段',
    `relevance_score` DECIMAL(5,4) NOT NULL COMMENT '该证据对本文资源的相关度',
    `usage_type` ENUM('direct_quote', 'paraphrase', 'conceptual', 'example') NOT NULL COMMENT '引用类型',
    `verified_status` ENUM('pending', 'verified', 'rejected', 'replaced') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    `verified_by` INT UNSIGNED NULL COMMENT '审核教师用户 ID',
    `verified_at` DATETIME NULL COMMENT '审核时间',
    `source_page` INT NULL COMMENT '来源页码',
    `source_paragraph` INT NULL COMMENT '来源段落序号',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX `idx_resource_id` (`resource_id`),
    INDEX `idx_chunk_id` (`chunk_id`),
    INDEX `idx_kp_id` (`kp_id`),
    INDEX `idx_verified_status` (`verified_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资源与证据 Chunk 关联表';

-- ----------------------------------------------------------
-- 视图：证据汇总（方便教师审核）
-- ----------------------------------------------------------
CREATE OR REPLACE VIEW `v_resource_evidence_summary` AS
SELECT
    rel.link_id,
    rel.resource_id,
    rr.resource_title,
    rel.quote_text,
    rel.usage_type,
    rel.verified_status,
    rel.relevance_score,
    kp.kp_name,
    cmc.filename,
    rel.source_page,
    rel.source_paragraph,
    rel.created_at,
    rel.verified_by,
    rel.verified_at
FROM `resource_evidence_links` rel
JOIN `learning_resources` rr ON rel.resource_id = rr.resource_id
JOIN `knowledge_points` kp ON rel.kp_id = kp.kp_id
JOIN `course_material_chunks` cmc ON rel.chunk_id = cmc.chunk_id
WHERE rr.is_deleted = 0 AND cmc.is_deleted = 0;

-- ----------------------------------------------------------
-- 视图：待审核的知识点-Chunk 匹配
-- ----------------------------------------------------------
CREATE OR REPLACE VIEW `v_pending_kp_chunk_links` AS
SELECT
    l.link_id,
    l.chunk_id,
    l.kp_id,
    kp.kp_name,
    kp.course_id,
    c.filename AS material_filename,
    c.course_id AS material_course_id,
    l.match_method,
    l.relevance_score,
    l.status,
    l.created_at
FROM `kp_chunk_links` l
JOIN `knowledge_points` kp ON l.kp_id = kp.kp_id
JOIN `course_material_chunks` cc ON l.chunk_id = cc.chunk_id
JOIN `course_materials` c ON cc.material_id = c.material_id
WHERE l.status = 'pending'
  AND kp.is_deleted = 0
  AND cc.is_deleted = 0
  AND c.is_deleted = 0;
