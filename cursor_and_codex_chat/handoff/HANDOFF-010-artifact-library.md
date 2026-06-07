# HANDOFF-010：Stage-10 成果库与分支合并模块

## 任务状态

**完成** — Stage-10 成果库与分支合并模块已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/artifact_repo.py` | 新建 | 成果库与分支合并所有 SQL |
| `backend/app/services/artifact_service.py` | 新建 | 成果库与分支合并业务逻辑 |
| `backend/app/routers/artifacts.py` | 新建 | API 路由 |
| `backend/app/main.py` | 修改 | 注册 `artifacts.router` |
| `cursor_and_codex_chat/handoff/HANDOFF-010-artifact-library.md` | 新建 | 本交接报告 |

**说明**：未修改 `task_service.py`、`task_repo.py`、`review_service.py`、`review_repo.py`、`database/*`、`frontend/*`、`docs/*`。

---

## 二、实现内容

### 2.1 Repository 层（`artifact_repo.py`）

| 函数 | 说明 |
|---|---|
| `get_output_for_adoption` | 查询输出上下文（成果采用校验）|
| `has_adopted_output` | 检查 output 是否已被采用 |
| `get_adopted_output_by_id` | 按 adopted_id 查询成果详情（联表）|
| `list_project_artifacts` | 分页查询项目成果列表 |
| `get_branch_context` | 查询分支上下文（分支合并校验）|
| `get_task_context` | 查询任务上下文 |
| `get_output_context` | 查询输出上下文 |
| `create_adopted_output` | 创建成果采用记录 |
| `update_output_status_adopted` | 更新 output 状态为 adopted |
| `update_task_status_adopted` | 更新 task 状态为 adopted |
| `get_next_version_no` | 事务内生成下一个 version_no |
| `create_task_output` | 创建新 output（manual_merge 用）|
| `update_output_status` | 更新 output 状态（通用）|
| `update_branch_status` | 更新分支状态 |
| `create_merge_record` | 创建分支合并记录 |
| `is_user_project_leader/teacher/in_project/is_admin` | 权限判断 |
| `get_adopted_output_project_context` | 从 adopted_id 获取 project_id |

### 2.2 Service 层（`artifact_service.py`）

| 函数 | 说明 |
|---|---|
| `adopt_output` | 成果采用事务 |
| `list_project_artifacts` | 项目成果列表 |
| `get_artifact_detail` | 成果详情 |
| `merge_branches` | 分支合并事务（支持四种策略）|
| `_can_adopt_or_merge` | 采用/合并权限判断 |

### 2.3 Router 层（`artifacts.py`）

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/outputs/{output_id}/adopt` | 采用成果 |
| GET | `/api/projects/{project_id}/artifacts` | 项目成果列表 |
| GET | `/api/artifacts/{adopted_id}` | 成果详情 |
| POST | `/api/tasks/{task_id}/branches/merge` | 分支合并 |

---

## 三、数据库是否变化

**否**。未修改 `database/*`，未修改表结构。

涉及数据表：

| 表 | 操作 |
|---|---|
| `adopted_outputs` | INSERT |
| `task_outputs` | UPDATE（status → adopted/generated）|
| `project_tasks` | UPDATE（status → adopted）|
| `task_branches` | UPDATE（status → merged/active）|
| `merge_records` | INSERT |
| `operation_logs` | INSERT |

---

## 四、新增接口列表

```
POST   /api/outputs/{output_id}/adopt
GET    /api/projects/{project_id}/artifacts
GET    /api/artifacts/{adopted_id}
POST   /api/tasks/{task_id}/branches/merge
```

---

## 五、成果采用事务说明

```python
with get_db_transaction() as conn:
    # 1. 检查未重复采用
    adopted = artifact_repo.has_adopted_output(output_id, conn)
    if adopted:
        conn.rollback()
        raise ConflictException(...)

    # 2. 插入 adopted_outputs
    adopted_id = artifact_repo.create_adopted_output(...)

    # 3. 更新 task_outputs.status = 'adopted'（检查 affected_rows）
    affected = artifact_repo.update_output_status_adopted(output_id, conn)
    if affected == 0:
        conn.rollback()
        raise NotFoundException(...)

    # 4. 更新 project_tasks.status = 'adopted'（检查 affected_rows）
    affected = artifact_repo.update_task_status_adopted(task_id, conn)
    if affected == 0:
        conn.rollback()
        raise NotFoundException(...)

    # 5. 写入 operation_logs
    user_repo.insert_operation_log_with_conn(...)

    conn.commit()
```

---

## 六、adopted_outputs 写入说明

```python
artifact_repo.create_adopted_output(
    project_id=project_id,
    task_id=task_id,
    output_id=output_id,
    artifact_title=artifact_title,
    artifact_type=artifact_type,
    release_version=release_version,
    adopted_by=user_id,
    conn=conn,
)
```

- `adopted_by` = 当前用户
- `adopted_at` = 当前时间
- `is_deleted` = 0（默认）
- `adopted_id` = `cursor.lastrowid`

---

## 七、task_outputs 状态更新说明

| 操作 | 状态 |
|---|---|
| 成果采用 | → `adopted` |
| adopt_source | → `adopted` |
| adopt_target | → `adopted` |
| manual_merge | → 新建 output，`status = 'generated'` |
| adopt_separately | 无更新 |

`affected_rows == 0` 时 rollback。

---

## 八、project_tasks 状态更新说明

| 操作 | 状态 |
|---|---|
| 成果采用 | → `adopted` |
| 分支合并 | 无自动更新（按业务需求可选） |

`affected_rows == 0` 时 rollback。

---

## 九、分支合并策略说明

| 策略 | 行为 |
|---|---|
| `adopt_source` | source_output 状态更新为 adopted，不创建新 output |
| `adopt_target` | target_output 状态更新为 adopted，不创建新 output |
| `manual_merge` | 创建新 task_output（source_type=manual_merge），更新 source_branch → merged，target_branch → active，返回 merged_output_id |
| `adopt_separately` | source_branch → merged，记录即可，不创建新 output |

`manual_merge` 特殊处理：

```python
merged_output_id = artifact_repo.create_task_output(
    task_id=task_id,
    output_title=merged_output_title.strip(),
    content=merged_content,
    source_type="manual_merge",
    parent_output_id=target_output_id_resolved,
    created_by=user_id,
    conn=conn,
)
```

version_no 在事务内通过 `get_next_version_no()` 生成（`MAX(version_no) + 1`）。

---

## 十、merge_records 写入说明

```python
artifact_repo.create_merge_record(
    project_id=project_id,
    task_id=task_id,
    base_output_id=base_output_id,
    source_output_id=source_output_id_resolved,
    target_output_id=target_output_id_resolved,
    merged_output_id=merged_output_id,
    merge_strategy=merge_strategy,
    merge_comment=merge_note,
    merged_by=user_id,
    conn=conn,
)
```

- `merge_id` = `cursor.lastrowid`
- 所有字段均在事务内写入

---

## 十一、task_branches 状态更新说明

| 策略 | source_branch | target_branch |
|---|---|---|
| `adopt_source` | 无 | 无 |
| `adopt_target` | 无 | 无 |
| `manual_merge` | → `merged` | → `active` |
| `adopt_separately` | → `merged` | 无 |

---

## 十二、operation_logs 写入说明

| 操作 | action_type | action_desc 示例 |
|---|---|---|
| 成果采用 | `artifact:adopt` | `采用成果: output=1, artifact=需求分析` |
| 分支合并 | `branch:merge` | `分支合并: task=1, strategy=manual_merge, merge_id=2` |

所有日志与业务操作在同一事务内。

---

## 十三、权限规则说明

### 成果采用权限

| 角色 | 能否采用 |
|---|---|
| admin | 可以 |
| 项目 leader | 可以 |
| 项目 teacher | 可以 |
| 项目 reviewer | **不能** |
| 普通 member | **不能** |
| 非项目成员 | **不能** |

### 成果列表权限

| 角色 | 能否查看 |
|---|---|
| admin | 全部 |
| 项目成员 | 本项目 |
| 非项目成员 | **不能** |

### 分支合并权限（与成果采用一致）

| 角色 | 能否合并 |
|---|---|
| admin | 可以 |
| 项目 leader | 可以 |
| 项目 teacher | 可以 |
| 其他 | **不能** |

### 成果详情权限

| 角色 | 能否查看 |
|---|---|
| admin | 全部 |
| 项目成员 | 本项目 |
| 非项目成员 | **不能** |

---

## 十四、采用成果测试方法

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<USER>","password":"<PWD>"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

# 假设 output_id=5，状态已 approved
curl -X POST "http://127.0.0.1:8000/api/outputs/5/adopt" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "artifact_title": "数据库课程设计需求分析",
    "artifact_type": "report_section",
    "release_version": "v1.0",
    "adopt_note": "采用审核通过版本"
  }'
```

期望：
```json
{"code": 0, "message": "success", "data": {"adopted_id": 1}}
```

---

## 十五、成果列表测试方法

```bash
# 查询项目 1 的成果
curl "http://127.0.0.1:8000/api/projects/1/artifacts?page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"

# 按类型过滤
curl "http://127.0.0.1:8000/api/projects/1/artifacts?artifact_type=report_section" \
  -H "Authorization: Bearer $TOKEN"

# 按关键词搜索
curl "http://127.0.0.1:8000/api/projects/1/artifacts?keyword=需求" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十六、成果详情测试方法

```bash
curl "http://127.0.0.1:8000/api/artifacts/1" \
  -H "Authorization: Bearer $TOKEN"
```

期望返回完整成果信息（含 output_content）。

---

## 十七、分支合并测试方法

```bash
# manual_merge
curl -X POST "http://127.0.0.1:8000/api/tasks/1/branches/merge" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "source_branch_id": 2,
    "target_branch_id": 1,
    "source_output_id": 8,
    "target_output_id": 5,
    "merge_strategy": "manual_merge",
    "merged_output_title": "需求分析合并版",
    "merged_content": "合并后的正文内容",
    "merge_note": "综合两个分支的内容形成最终版"
  }'

# adopt_source
curl -X POST "http://127.0.0.1:8000/api/tasks/1/branches/merge" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "source_branch_id": 2,
    "target_branch_id": 1,
    "source_output_id": 8,
    "merge_strategy": "adopt_source",
    "merge_note": "采用源分支版本"
  }'
```

期望：
```json
{"code": 0, "message": "success", "data": {"merge_id": 1, "merged_output_id": 9}}
```

---

## 十八、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查

---

## 十九、是否实现统计看板

**否**。

---

## 二十、是否实现前端页面

**否**。

---

## 二十一、需要 Codex 审查的重点

1. **成果采用前状态校验**：output 状态必须为 approved，是否正确拦截非 approved 状态
2. **重复采用拦截**：`has_adopted_output` 在事务内检查，失败 rollback
3. **affected_rows 检查**：成果采用和分支合并中所有关键 UPDATE 是否检查 affected_rows
4. **manual_merge 条件**：merged_output_title 和 merged_content 是否正确校验非空
5. **merge_strategy 白名单**：`VALID_MERGE_STRATEGIES` 是否只包含四种允许值
6. **分支归属校验**：source_branch/target_branch 是否正确校验属于同一 task
7. **output 归属校验**：source_output/target_output 是否正确校验属于同一 task
8. **权限规则**：`adopt_output` 和 `merge_branches` 是否只允许 admin/leader/teacher
9. **成果列表权限**：非项目成员是否被正确拒绝
10. **事务一致性**：所有写操作是否在同一事务内，失败是否正确 rollback
11. **SQL 集中**：`artifact_repo.py` 是否包含所有相关 SQL，service 层无内联 SQL
12. **参数化**：所有 SQL 是否使用 `%s` 参数绑定，无字符串拼接
13. **无越界**：确认未实现统计看板、前端页面、未修改 database/

---

## 二十二、验收清单

- [x] `POST /api/outputs/{output_id}/adopt` 实现（成果采用事务）
- [x] `GET /api/projects/{project_id}/artifacts` 实现（分页 + 类型过滤 + 关键词搜索）
- [x] `GET /api/artifacts/{adopted_id}` 实现（含 output content）
- [x] `POST /api/tasks/{task_id}/branches/merge` 实现（四种策略）
- [x] `adopted_outputs` 写入
- [x] `merge_records` 写入
- [x] `task_outputs` 状态更新（adopted/generated）
- [x] `task_branches` 状态更新（merged/active）
- [x] `operation_logs` 写入（artifact:adopt、branch:merge）
- [x] 成果采用：output 状态必须为 approved
- [x] 成果采用：不允许重复采用
- [x] 所有写操作在同一事务内
- [x] affected_rows 检查
- [x] 权限规则：admin/leader/teacher 可采用/合并
- [x] SQL 集中于 artifact_repo.py
- [x] 参数化 SQL
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`
- [x] Python 语法检查通过

---

**本阶段完成后停止，等待 Codex 审查。**
