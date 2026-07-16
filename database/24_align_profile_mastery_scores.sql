-- Keep the denormalized profile summary aligned with per-knowledge-point mastery.
USE `ai_collab_audit_system`;

UPDATE `student_profiles` sp
SET sp.`mastery_score` = COALESCE(
    (
        SELECT AVG(skm.`mastery_level`)
        FROM `student_knowledge_mastery` skm
        WHERE skm.`profile_id` = sp.`profile_id`
          AND skm.`is_deleted` = 0
    ),
    sp.`mastery_score`
)
WHERE sp.`is_deleted` = 0;
