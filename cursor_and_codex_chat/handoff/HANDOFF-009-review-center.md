# HANDOFF-009：Stage-09 审核中心模块

## 任务状态

**完成** — Stage-09 审核中心模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/review_repo.py` | 新建 | 审核相关所有 SQL |
| `backend/app/services/review_service.py` | 新建 | 审核业务逻辑 |
| `backend/app/routers/reviews.py` | 新建 | API 路由 |
| `backend/app/main.py` | 修改 | 注册 reviews router |
| `cursor_and_codex_chat/handoff/HANDOFF-009-review-center.md` | 新建 | 本交接报告 |

**说明**：`main.py` 的修改仅为注册 `reviews.router`，符合允许修改范围。

---

## 二、实现内容

### 2.1 Repository 层（`review_repo.py`）

| 函数 | 说明 |
|---|---|
| `get_review_request_by_id` | 按 ID 查询审核请求详情（联表）|
| `get_request_project_context` | 获取审核请求项目上下文（用于权限判断）|
| `list_pending_reviews` | 分页查询待审核列表 |
| `get_output_project_context` | 获取输出项目上下文 |
| `get_output_by_id` | 按 ID 查询输出（含 content）|
| `is_user_project_leader/teacher/reviewer/in_project` | 项目内角色判断 |
| `list_issue_tags` | 查询所有可用问题标签 |
| `check_issue_tags_exist` | 批量校验问题标签是否存在 |
| `create_review_request` | 创建审核请求 |
| `has_pending_request` | 检查是否存在 pending 审核请求 |
| `update_review_request_status` | 更新审核请求状态 |
| `update_output_status` | 更新输出版本状态 |
| `update_task_status` | 更新项目任务状态 |
| `create_output_review` | 创建审核评分记录 |
| `create_output_issue_relation` | 创建问题标签关联记录 |

### 2.2 Service 层（`review_service.py`）

| 函数 | 说明 |
|---|---|
| `submit_for_review` | 提交审核事务 |
| `list_pending_reviews` | 待审核列表 |
| `get_review_detail` | 审核详情 |
| `complete_review` | 完成审核事务 |
| `_can_complete_review` | 审核权限判断 |
| `list_issue_tags` | 问题标签列表 |

### 2.3 Router 层（`reviews.py`）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/outputs/{output_id}/submit-review` | 提交审核 |
| GET | `/api/reviews/pending` | 待审核列表 |
| GET | `/api/reviews/{request_id}` | 审核详情 |
| POST | `/api/reviews/{request_id}/complete` | 完成审核 |
| GET | `/api/issue-tags` | 问题标签列表 |

---

## 三、数据库是否变化

**否**。未修改 `database/*`，未修改表结构。

涉及数据表：

| 表 | 操作 |
|---|---|
| `review_requests` | INSERT、UPDATE |
| `task_outputs` | UPDATE |
| `project_tasks` | UPDATE |
| `output_reviews` | INSERT |
| `output_issue_relations` | INSERT |
| `operation_logs` | INSERT |

---

## 四、新增接口列表

```
POST   /api/outputs/{output_id}/submit-review
GET    /api/reviews/pending
GET    /api/reviews/{request_id}
POST   /api/reviews/{request_id}/complete
GET    /api/issue-tags
```

---

## 五、输出提交审核事务说明

```python
with get_db_transaction() as conn:
    # 1. 检查无 pending 请求
    has_pending = review_repo.has_pending_request(output_id, conn)
    if has_pending:
        conn.rollback()
        raise ConflictException(...)

    # 2. 插入 review_requests
    request_id = review_repo.create_review_request(...)

    # 3. 更新 task_outputs.status = 'submitted'
    review_repo.update_output_status(output_id=output_id, status='submitted', conn=conn)

    # 4. 更新 project_tasks.status = 'submitted'
    review_repo.update_task_status(task_id=task_id, status='submitted', conn=conn)

    # 5. 写入 operation_logs
    user_repo.insert_operation_log_with_conn(...)

    conn.commit()
```

---

## 六、完成审核事务说明

```python
with get_db_transaction() as conn:
    # 1. 插入 output_reviews
    review_id = review_repo.create_output_review(...)

    # 2. 更新 review_requests.request_status
    review_repo.update_review_request_status(...)

    # 3. 更新 task_outputs.status（按 review_status）
    review_repo.update_output_status(output_id, status=review_status, conn=conn)

    # 4. 更新 project_tasks.status（按 review_status）
    review_repo.update_task_status(task_id, status=review_status, conn=conn)

    # 5. 写入 output_issue_relations（如有 issue_tag_ids）
    for tag_id in issue_tag_ids:
        review_repo.create_output_issue_relation(...)

    # 6. 写入 operation_logs
    user_repo.insert_operation_log_with_conn(...)

    conn.commit()
```

---

## 七、审核权限规则说明

### 提交审核权限
- 项目成员可提交
- 非项目成员不能提交

### 待审核列表权限
| 角色 | 可查看范围 |
|---|---|
| admin | 全部 pending |
| 项目内 leader/teacher/reviewer | 本项目 pending |
| 普通 member | 不能查看 |

### 完成审核权限
| 角色 | 可完成审核 |
|---|---|
| admin | 任意 |
| 指定 reviewer | 指定的审核请求 |
| 项目内 leader | 本项目 |
| 项目内 teacher | 本项目 |
| 项目内 reviewer | 本项目 |

### 审核详情权限
- 必须是有权访问该审核请求所属项目的用户

所有权限均基于 `project_members.project_role`（项目内角色），不依赖全局角色字符串。

---

## 八、状态流转规则说明

| review_status | review_requests.request_status | task_outputs.status | project_tasks.status |
|---|---|---|---|
| `approved` | `approved` | `approved` | `approved` |
| `rejected` | `rejected` | `rejected` | `rejected` |
| `revision_required` | `revision_required` | `revision_required` | `revision_required` |

三种状态均使用 Schema 允许值。

---

## 九、issue_tag_ids 如何校验

```python
if issue_tag_ids:
    all_exist, _ = review_repo.check_issue_tags_exist(issue_tag_ids)
    if not all_exist:
        raise ValidationException(message="存在无效或已删除的问题标签")
```

`check_issue_tags_exist` 批量查询 `issue_tags` 表，确认所有 tag_id 均存在且 `is_deleted = 0`。

---

## 十、output_issue_relations 写入说明

```python
if issue_tag_ids:
    for tag_id in issue_tag_ids:
        review_repo.create_output_issue_relation(
            output_id=output_id,
            review_id=review_id,
            tag_id=tag_id,
            created_by=user_id,
            conn=conn,
        )
```

- 每个 tag_id 一条记录
- 与其他写操作在同一事务内
- `is_deleted = 0` 由 SQL 默认写入

---

## 十一、operation_logs 写入说明

| 操作 | action_type | action_desc 示例 |
|---|---|---|
| 提交审核 | `review:submit` | `提交审核: output=1` |
| 完成审核 | `review:complete` | `完成审核: request=1, status=approved` |

所有日志与业务操作在同一事务内。

---

## 十二、提交审核测试方法

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<USER>","password":"<PASSWORD>"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 假设 output_id=1, reviewer_id=3
curl -X POST "http://127.0.0.1:8000/api/outputs/1/submit-review" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"reviewer_id":3,"submit_note":"请审核需求分析部分"}'
```

期望：
```json
{"code": 0, "message": "success", "data": {"request_id": 1}}
```

---

## 十三、待审核列表测试方法

```bash
# 全部待审核
curl "http://127.0.0.1:8000/api/reviews/pending?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# 指定项目
curl "http://127.0.0.1:8000/api/reviews/pending?project_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

期望：
```json
{
  "code": 0, "message": "success",
  "data": {
    "items": [...],
    "total": 3,
    "page": 1,
    "page_size": 10
  }
}
```

---

## 十四、完成审核测试方法

```bash
# 假设 request_id=1, review_status=approved
curl -X POST "http://127.0.0.1:8000/api/reviews/1/complete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "review_status": "approved",
    "accuracy_score": 9,
    "completeness_score": 8.5,
    "logic_score": 9,
    "format_score": 8,
    "usability_score": 9,
    "risk_score": 1,
    "review_comment": "整体可用，建议补充非功能需求。",
    "issue_tag_ids": [1, 3]
  }'
```

期望：
```json
{"code": 0, "message": "success", "data": {"review_id": 1}}
```

---

## 十五、问题标签关联测试方法

```bash
# 查询所有可用标签
curl "http://127.0.0.1:8000/api/issue-tags" \
  -H "Authorization: Bearer $TOKEN"

# 带 issue_tag_ids 的完成审核（见上节）
```

期望标签列表：
```json
{
  "code": 0, "message": "success",
  "data": [
    {"tag_id": 1, "tag_name": "逻辑错误", "tag_code": "LOGIC_ERROR", "severity": 3},
    {"tag_id": 2, "tag_name": "格式问题", "tag_code": "FORMAT", "severity": 1}
  ]
}
```

---

## 十六、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查

---

## 十七、是否实现成果库

**否**。

---

## 十八、是否实现统计看板

**否**。

---

## 十九、是否实现前端页面

**否**。

---

## 二十、需要 Codex 审查的重点

1. **提交审核事务**：是否在同一事务内完成 `review_requests` 插入、`task_outputs` 状态更新、`project_tasks` 状态更新、`operation_logs` 写入；`has_pending_request` 是否在事务内检查
2. **完成审核事务**：是否在同一事务内完成 `output_reviews` 插入、三个状态更新、`output_issue_relations` 写入（如有）、`operation_logs` 写入
3. **审核权限**：`review_requests` 表无 reviewer 时是否允许 leader/teacher/reviewer 完成；是否基于 `project_members.project_role` 而非全局角色
4. **状态流转**：三种 `review_status` 是否正确映射到三个表的状态
5. **issue_tag_ids**：校验是否确保所有 tag 存在且未删除
6. **重复提交拦截**：`has_pending_request` 是否在事务内检查
7. **affected_rows 检查**：`update_*_status` 是否被 service 层检查
8. **SQL 集中**：`review_repo.py` 是否包含所有审核相关 SQL，service 层无内联 SQL
9. **参数化**：所有 SQL 是否使用 `%s` 参数绑定，无字符串拼接
10. **无越界**：确认未实现成果库、统计看板、前端页面

---

## 二十一、验收清单

- [x] `POST /api/outputs/{output_id}/submit-review` 实现
- [x] `GET /api/reviews/pending` 实现（分页 + 项目过滤）
- [x] `GET /api/reviews/{request_id}` 实现（含 output content）
- [x] `POST /api/reviews/{request_id}/complete` 实现
- [x] `GET /api/issue-tags` 实现
- [x] `output_reviews` 写入
- [x] `output_issue_relations` 写入
- [x] `review_requests`、`task_outputs`、`project_tasks` 状态更新
- [x] `operation_logs` 写入
- [x] 所有写操作与日志同一事务
- [x] 审核权限基于项目内角色（leader/teacher/reviewer）
- [x] 重复提交拦截（pending 检查在事务内）
- [x] 所有 SQL 参数化，在 `review_repo.py`
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`
- [x] Python 语法检查通过

---

**本阶段完成后停止，不进入 Stage-10。**
