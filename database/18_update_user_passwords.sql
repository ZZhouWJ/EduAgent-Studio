-- 统一演示账号初始密码为 Pass@1234。
-- 生产部署必须在首次登录后更换，并禁止保留本脚本中的演示密码。

UPDATE `users`
SET `password_hash` = '$2b$12$Qcnez8qsfbryeJTPA/STAuHy64Rwz2IZOMXjYR4C5VgxkkvtBx4/y'
WHERE `username` IN ('admin', 'teacher_li', 'student_zhang', 'student_liu', 'student_chen');
