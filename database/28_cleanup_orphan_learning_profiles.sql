-- Exclude legacy learning profiles whose user account no longer exists.
USE `ai_collab_audit_system`;

UPDATE student_profiles sp
LEFT JOIN users u
  ON u.user_id = sp.student_id
 AND u.is_deleted = 0
SET sp.is_deleted = 1,
    sp.updated_at = NOW()
WHERE sp.is_deleted = 0
  AND u.user_id IS NULL;

UPDATE learning_task_progress p
LEFT JOIN users u
  ON u.user_id = p.student_id
 AND u.is_deleted = 0
SET p.is_deleted = 1,
    p.updated_at = NOW()
WHERE p.is_deleted = 0
  AND u.user_id IS NULL;
