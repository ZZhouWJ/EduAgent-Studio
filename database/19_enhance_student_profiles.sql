-- 扩展学生画像维度，兼容已初始化的 MySQL 5.7/8.x 数据库。
DROP PROCEDURE IF EXISTS `add_student_profile_column`;

DELIMITER $$
CREATE PROCEDURE `add_student_profile_column`(
    IN p_column_name VARCHAR(64),
    IN p_column_definition TEXT
)
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'student_profiles'
          AND COLUMN_NAME = p_column_name
    ) THEN
        SET @ddl = CONCAT(
            'ALTER TABLE `student_profiles` ADD COLUMN `',
            p_column_name,
            '` ',
            p_column_definition
        );
        PREPARE statement FROM @ddl;
        EXECUTE statement;
        DEALLOCATE PREPARE statement;
    END IF;
END$$
DELIMITER ;

CALL `add_student_profile_column`('knowledge_base', 'TEXT NULL COMMENT ''已有知识基础'' AFTER `learning_goal`');
CALL `add_student_profile_column`('cognitive_style', 'VARCHAR(100) NULL COMMENT ''认知与学习风格'' AFTER `current_level`');
CALL `add_student_profile_column`('time_constraints', 'VARCHAR(255) NULL COMMENT ''学习时间约束描述'' AFTER `cognitive_style`');
CALL `add_student_profile_column`('practice_level', 'VARCHAR(100) NULL COMMENT ''实践能力水平'' AFTER `time_constraints`');
CALL `add_student_profile_column`('motivation', 'VARCHAR(255) NULL COMMENT ''学习动机'' AFTER `practice_level`');
CALL `add_student_profile_column`('error_prone_points', 'JSON NULL COMMENT ''易错点列表'' AFTER `motivation`');

DROP PROCEDURE `add_student_profile_column`;
