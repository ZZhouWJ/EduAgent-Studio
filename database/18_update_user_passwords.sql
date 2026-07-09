-- 重置用户密码为：用户名+123456
-- 密码格式：admin123456, teacher01123456, student01123456, student02123456, student03123456

UPDATE `users` SET `password_hash` = '$2b$12$Xia.y8ZIpcBVXPqy3AsWbegsA/Z3NmKEwGtKNUCMr7BQJpNN3gcu2' WHERE `username` = 'admin';
UPDATE `users` SET `password_hash` = '$2b$12$XT7MynMTbfbXlHHf6k85F.i.BKu5vqVXi90cdtfqBxnSb.mvvMBmG' WHERE `username` = 'teacher01';
UPDATE `users` SET `password_hash` = '$2b$12$xc2pBOBuryb5Mt5cVt7WSejawfEef4yYWv8B0Zt8JEmHhdo8S6NVG' WHERE `username` = 'student01';
UPDATE `users` SET `password_hash` = '$2b$12$0wln8CTLXjc26LZelKXcDOZQo/zqfngdAUjId.Q6T9SUU2lBZ1ota' WHERE `username` = 'student02';
UPDATE `users` SET `password_hash` = '$2b$12$VMQgsECcF0NBg1pooXHpNeXqW0RrWhH5rwl7WHPuTZZHEb2qBhM7G' WHERE `username` = 'student03';
