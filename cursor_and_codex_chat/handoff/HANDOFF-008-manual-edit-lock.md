# HANDOFF-008：Stage-08 人工编辑、批注与乐观锁模块

## 任务状态

**完成** — Stage-08 人工编辑、批注与乐观锁模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/task_repo.py` | 修改（追加） | 新增 8 个 SQL 函数 |
| `backend/app/services/task_service.py` | 修改（追加） | 新增 5 个业务函数 + 1 个辅助函数 |
| `backend/app/routers/tasks.py` | 修改（追加） | 新增 5 个路由 + 4 个请求模型 |
| `cursor_and_codex_chat/handoff/HANDOFF-008-manual-edit-lock.md` | 新建 | 本交接报告 |

**说明**：Stage-07 允许修改的文件列表包含 `task_repo.py`、`task_service.py`、`tasks.py`，因此在此范围内。

---

## 二、实现内容

### 2.1 Repository 层新增函数（`task_repo.py`）

| 函数 | 说明 |
|---|---|
| `update_output_with_lock` | 乐观锁更新输出，WHERE 含 output_id + lock_version + is_deleted=0 |
| `get_output_project_id` | 通过 output_id 获取 project_id |
| `save_output_as_new_version` | 基于已有输出创建新版本（parent_output_id = source_output_id）|
| `list_output_comments` | 查询输出批注列表（支持 status 过滤）|
| `get_comment_output_id` | 通过 comment_id 获取 output_id |
| `get_comment_by_id` | 按 ID 查询批注详情 |
| `create_output_comment` | 创建输出批注 |
| `update_comment_status` | 更新批注状态 |

### 2.2 Service 层新增函数（`task_service.py`）

| 函数 | 说明 |
|---|---|
| `update_output` | 乐观锁更新输出版本事务 |
| `save_output_as_new_version` | 另存为新版本事务 |
| `list_output_comments` | 批注列表（权限校验）|
| `create_output_comment` | 新增批注事务 |
| `update_comment_status` | 批注状态更新事务 |

### 2.3 Router 层新增接口（`tasks.py`）

| 方法 | 路径 | 说明 |
|---|---|---|
| PUT | `/api/outputs/{output_id}` | 编辑输出版本（乐观锁）|
| POST | `/api/outputs/{output_id}/save-as` | 另存为新版本 |
| GET | `/api/outputs/{output_id}/comments` | 批注列表 |
| POST | `/api/outputs/{output_id}/comments` | 新增批注 |
| PUT | `/api/comments/{comment_id}/status` | 批注状态更新 |

---

## 三、数据库是否变化

**否**。未修改 `database/*`，未修改表结构。

涉及数据表：

| 表 | 操作 |
|---|---|
| `task_outputs` | UPDATE（乐观锁）、INSERT（另存为）|
| `output_comments` | INSERT、UPDATE、SELECT |
| `operation_logs` | INSERT |

---

## 四、新增接口列表

```
PUT    /api/outputs/{output_id}
POST   /api/outputs/{output_id}/save-as
GET    /api/outputs/{output_id}/comments
POST   /api/outputs/{output_id}/comments
PUT    /api/comments/{comment_id}/status
```

---

## 五、乐观锁实现说明

```sql
UPDATE task_outputs
SET content = %s,
    edit_summary = %s,
    lock_version = lock_version + 1,
    last_modified_at = %s,
    last_modified_by = %s,
    updated_at = %s,
    updated_by = %s
WHERE output_id = %s
  AND lock_version = %s          -- 乐观锁条件
  AND is_deleted = 0
```

- WHERE 包含 `output_id` + `lock_version`（客户端传入）+ `is_deleted = 0`
- 更新后 `lock_version + 1`
- `last_modified_at` 和 `updated_at` 均更新为当前时间
- `last_modified_by` 和 `updated_by` 均更新为当前用户

---

## 六、affected_rows = 0 时如何处理

```python
affected = task_repo.update_output_with_lock(...)
if affected == 0:
    conn.rollback()
    raise ConflictException(
        message="当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。"
    )
```

`ConflictException` 继承 `AppException`，错误码固定为 `4004`，与任务要求的冲突错误码一致。

---

## 七、另存为新版本如何设置 parent_output_id

```python
new_output_id = task_repo.save_output_as_new_version(
    source_output_id=output_id,          # 原 output_id 作为 parent_output_id
    task_id=task_id,
    branch_id=(branch_id if branch_id is not None else source_output["branch_id"]),
    version_no=next_version,
    output_title=output_title.strip(),
    content=content,
    edit_summary=edit_summary,
    source_type="hybrid",                 # 固定为 hybrid
    created_by=user_id,
    conn=conn,
)
```

- `parent_output_id` = 原 `output_id`（通过 `source_output_id` 参数传入）
- `source_type` = `"hybrid"`（表示人工编辑）
- `version_no` 在事务内通过 `FOR UPDATE` 锁生成
- `lock_version` 初始为 0

---

## 八、version_no 是否在事务内生成

**是**。在 `save_output_as_new_version` 的事务中，先调用 `get_next_version_no_for_update`，再调用 `save_output_as_new_version`，两者使用同一个 `conn`。

```python
with get_db_transaction() as conn:
    next_version = task_repo.get_next_version_no_for_update(task_id=task_id, conn=conn)
    new_output_id = task_repo.save_output_as_new_version(..., version_no=next_version, conn=conn)
    conn.commit()
```

---

## 九、output_comments 写入说明

```python
# 新增批注
comment_id = task_repo.create_output_comment(
    output_id=output_id,
    commenter_id=user_id,
    comment_type=comment_type.strip(),
    comment_text=comment_text.strip(),
    conn=conn,
)
```

- `status` 默认 `"open"`
- `is_deleted` 默认 `0`
- 批注创建和日志在同一事务内

---

## 十、批注状态更新权限说明

| 角色 | 权限 |
|---|---|
| admin | 可更新 |
| teacher | 可更新 |
| project_leader | 可更新 |
| 批注创建人 | 可更新 |
| 普通项目成员 | 不可更新（仅能添加批注）|

```python
if _is_admin(user):
    pass
elif "teacher" in user.get("roles", []):
    pass
elif "project_leader" in user.get("roles", []):
    pass
elif comment["commenter_id"] == user_id:
    pass
else:
    raise ForbiddenException(message="无权更新此批注状态")
```

批注状态值：`open`、`resolved`、`closed`。

---

## 十一、operation_logs 写入说明

| 操作 | action_type | action_desc 示例 |
|---|---|---|
| 编辑输出 | `output:update` | `编辑输出版本: output=1` |
| 另存为新版本 | `output:save_as` | `另存为新版本: output=1 -> new_output=2` |
| 新增批注 | `output:comment` | `新增批注: output=1` |
| 更新批注状态 | `output:comment_status` | `更新批注状态: comment=1, status=resolved` |

所有日志与业务操作在同一事务内写入。

---

## 十二、编辑输出版本测试方法

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 假设 output_id=1, lock_version=0
curl -X PUT "http://127.0.0.1:8000/api/outputs/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"修改后的正文内容","lock_version":0,"edit_summary":"补充用户角色说明"}'
```

期望（成功）：
```json
{"code": 0, "message": "success", "data": {"output_id": 1, "lock_version": 1, ...}}
```

---

## 十三、乐观锁冲突测试方法

```bash
# 场景：用户 A 和用户 B 同时读取 lock_version=0，用户 A 先提交，用户 B 后提交

# 用户 B 的请求（lock_version 仍为 0，但数据库已变为 1）
curl -X PUT "http://127.0.0.1:8000/api/outputs/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"用户B的修改","lock_version":0,"edit_summary":"冲突修改"}'
```

期望（冲突）：
```json
{
  "code": 4004,
  "message": "当前内容已被其他成员修改，请刷新后重新编辑，或另存为新版本。",
  "data": null
}
```

---

## 十四、另存为新版本测试方法

```bash
# 假设 output_id=1
curl -X POST "http://127.0.0.1:8000/api/outputs/1/save-as" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"output_title":"需求分析人工修改版","content":"另存为新版本的正文","edit_summary":"基于 AI 初稿人工修改"}'
```

期望：
```json
{
  "code": 0, "message": "success",
  "data": {
    "output_id": 2,
    "parent_output_id": 1,
    "source_type": "hybrid",
    "version_no": 2,
    ...
  }
}
```

---

## 十五、批注新增和状态更新测试方法

```bash
# 新增批注
curl -X POST "http://127.0.0.1:8000/api/outputs/1/comments" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"comment_type":"修改建议","comment_text":"建议补充系统非功能需求。"}'

# 批注列表
curl "http://127.0.0.1:8000/api/outputs/1/comments" \
  -H "Authorization: Bearer $TOKEN"

# 更新批注状态（假设 comment_id=1）
curl -X PUT "http://127.0.0.1:8000/api/comments/1/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status":"resolved"}'
```

---

## 十六、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查
2. **另存为接口路径**：`POST /api/outputs/{output_id}/save-as`，接口契约文档中的建议路径为 `save-as`（非 `save-as-new-version`），以保持路径简洁

---

## 十七、是否实现审核中心

**否**。

---

## 十八、是否实现成果库

**否**。

---

## 十九、是否实现统计看板

**否**。

---

## 二十、是否实现前端页面

**否**。

---

## 二十一、需要 Codex 审查的重点

1. **乐观锁**：WHERE 条件是否包含 `output_id + lock_version + is_deleted = 0`，`affected_rows == 0` 时是否抛出 `ConflictException(code=4004)`
2. **另存为新版本**：`parent_output_id` 是否正确指向源 `output_id`，`source_type = hybrid`，`version_no` 是否在事务内生成
3. **批注权限**：状态更新是否仅限 admin/teacher/project_leader/批注创建人
4. **事务一致性**：编辑输出、另存为、批注新增、状态更新的数据库写操作是否与 `operation_logs` 在同一事务内
5. **无越界**：确认未实现审核中心、成果库、统计看板、前端页面
6. **SQL 集中**：所有 SQL 在 `task_repo.py`，service 层无内联 SQL
7. **参数化**：所有 SQL 使用 `%s` 参数绑定，无字符串拼接用户输入

---

## 二十二、验收清单

- [x] 编辑输出版本接口（乐观锁 PUT /api/outputs/{output_id}）
- [x] 另存为新版本接口（POST /api/outputs/{output_id}/save-as）
- [x] 乐观锁 WHERE 含 output_id + lock_version + is_deleted=0
- [x] affected_rows == 0 时抛出 ConflictException(code=4004)
- [x] version_no 在事务内 FOR UPDATE 生成
- [x] parent_output_id 指向源 output_id
- [x] 输出批注新增接口（POST /api/outputs/{output_id}/comments）
- [x] 输出批注列表接口（GET /api/outputs/{output_id}/comments）
- [x] 批注状态更新接口（PUT /api/comments/{comment_id}/status）
- [x] output_comments 写入
- [x] 批注状态更新权限控制（仅 admin/teacher/leader/创建人）
- [x] 人工编辑相关 operation_logs 写入
- [x] 所有写操作与日志同一事务
- [x] 所有 SQL 参数化，在 task_repo.py
- [x] 未修改 database/*、frontend/*、docs/*
- [x] Python 语法检查通过

---

**本阶段完成后停止，不进入 Stage-09。**
