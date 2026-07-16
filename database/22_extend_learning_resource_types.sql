-- Align the persisted resource type domain with the multi-agent workbench.
ALTER TABLE `learning_resources`
    MODIFY COLUMN `resource_type`
    ENUM(
        'lecture',
        'mindmap',
        'quiz',
        'case',
        'code_case',
        'ppt',
        'video_script',
        'experiment_report',
        'error_analysis',
        'learning_card',
        'review',
        'test',
        'other'
    ) NOT NULL COMMENT '资源类型';
