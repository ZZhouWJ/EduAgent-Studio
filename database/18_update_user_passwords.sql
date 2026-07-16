-- 清除旧版本中可公开推断的共享演示密码。
-- 运行 database/seed_demo_data.py 并通过 DEMO_PASSWORD 提供独立密码后，
-- 脚本会重新激活这些账号。

UPDATE `users`
SET `password_hash` = '!set-with-seed-script!',
    `status` = 'disabled'
WHERE `username` IN ('admin', 'teacher_li', 'student_zhang', 'student_liu', 'student_chen');
