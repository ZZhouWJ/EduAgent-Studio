# -*- coding: utf-8 -*-
import pymysql

conn = pymysql.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="061202",
    database="ai_collab_audit_system",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

with conn:
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE roles SET role_name='学生成员', description='项目普通成员，可以创建任务、提交输出、查看本项目内容'
            WHERE role_code='student_member'
        """)
        cursor.execute("""
            UPDATE roles SET role_name='项目负责人', description='项目负责人，可以审核本项目输出、添加成员、采纳成果'
            WHERE role_code='project_leader'
        """)
        cursor.execute("""
            UPDATE roles SET role_name='指导教师', description='指导教师，可以查看指导项目并添加意见、审核输出、采纳成果'
            WHERE role_code='teacher'
        """)
        cursor.execute("""
            UPDATE roles SET role_name='管理员', description='系统管理员，拥有全部权限'
            WHERE role_code='admin'
        """)
        conn.commit()

        cursor.execute("SELECT role_id, role_name, description FROM roles")
        rows = cursor.fetchall()
        print("Current roles in database:")
        for r in rows:
            print(f"  id={r['role_id']}, name={r['role_name']}, desc={r['description']}")
