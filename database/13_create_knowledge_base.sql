-- 课程知识库相关表
-- course_materials: 课程资料元数据
CREATE TABLE IF NOT EXISTS `course_materials` (
  `material_id` INT AUTO_INCREMENT PRIMARY KEY,
  `course_id` INT NOT NULL COMMENT '关联课程ID',
  `filename` VARCHAR(255) NOT NULL COMMENT '原始文件名',
  `file_type` VARCHAR(50) NOT NULL COMMENT 'pdf/markdown/word/ppt/txt',
  `storage_path` VARCHAR(500) NOT NULL COMMENT '文件存储路径',
  `status` VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/parsing/parsed/failed',
  `error_message` TEXT COMMENT '解析失败时的错误信息',
  `total_chunks` INT DEFAULT 0 COMMENT '生成的chunks数量',
  `created_by` INT NOT NULL COMMENT '上传用户ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` TINYINT DEFAULT 0,
  INDEX `idx_course_id` (`course_id`),
  INDEX `idx_status` (`status`),
  INDEX `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程资料元数据表';

-- course_material_chunks: 文档切分块
CREATE TABLE IF NOT EXISTS `course_material_chunks` (
  `chunk_id` INT AUTO_INCREMENT PRIMARY KEY,
  `material_id` INT NOT NULL COMMENT '关联资料ID',
  `course_id` INT NOT NULL COMMENT '关联课程ID',
  `kp_id` INT DEFAULT NULL COMMENT '关联知识点，可为空',
  `title` VARCHAR(255) COMMENT 'chunk标题/小节名',
  `content` TEXT NOT NULL COMMENT 'chunk正文内容',
  `source_page` INT DEFAULT NULL COMMENT '来源页码',
  `source_paragraph` INT DEFAULT NULL COMMENT '来源段落序号',
  `bm25_terms` TEXT COMMENT 'BM25检索关键词，逗号分隔',
  `chunk_index` INT NOT NULL COMMENT '在文档中的顺序',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `is_deleted` TINYINT DEFAULT 0,
  INDEX `idx_course_id` (`course_id`),
  INDEX `idx_material_id` (`material_id`),
  INDEX `idx_kp_id` (`kp_id`),
  INDEX `idx_bm25_terms` (`bm25_terms`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档切分块表';
