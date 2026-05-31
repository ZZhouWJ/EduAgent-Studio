# TASK-009-FIX 审核中心模块修复任务

## 任务状态

已完成。

## 任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-009-review-center.md` 修复 Stage-09 审查发现的阻塞问题。修复完成后提交 handoff，等待 Codex 复审。复审通过前不得进入 Stage-10。

## 允许修改文件

- `backend/app/routers/reviews.py`
- `backend/app/services/review_service.py`
- `backend/app/repositories/review_repo.py`
- `cursor_and_codex_chat/handoff/HANDOFF-009-FIX-review-center.md`

如确实需要复用任务或输出权限判断，可少量修改：

- `backend/app/services/task_service.py`
- `backend/app/repositories/task_repo.py`

但必须在 handoff 中说明理由。

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 成果库；
2. 统计看板；
3. 前端页面；
4. Stage-10 成果库与分支合并内容；
5. 写入 `adopted_outputs`；
6. 成果采用接口。

## 必须修复的问题

### 1. 提交审核时校验 reviewer_id

当前 `reviewer_id` 未校验，直接写入 `review_requests`。

修复要求：

1. 如果传入 `reviewer_id`，必须校验用户存在；
2. 必须校验 reviewer 属于当前项目，或具备项目内审核权限；
3. 不得允许跨项目 reviewer；
4. 不得让数据库外键错误替代业务校验；
5. 非法 reviewer 应返回统一参数错误或资源不存在错误。

### 2. 待审核列表支持指定 reviewer 普通成员查看

当前普通 member 即使被指定为 `reviewer_id`，也无法在待审核列表看到自己的请求。

修复要求：

1. 非 admin 的待审核列表应允许：
   - 项目内 leader / teacher / reviewer 查看本项目 pending；
   - `r.reviewer_id = 当前用户` 时查看分配给自己的 pending；
2. 不得泄露其他项目待审核记录；
3. `project_id` 过滤仍必须生效。

### 3. 完成审核状态只允许三种结论

当前完成审核使用包含 `pending` 的 `VALID_REVIEW_STATUS`。

修复要求：

1. 完成审核入参只允许：
   - `approved`
   - `rejected`
   - `revision_required`
2. `pending` 只能作为请求初始状态，不得作为完成审核结论；
3. 非法状态返回统一参数错误。

### 4. 指定 reviewer 场景收紧完成审核权限

当前指定 reviewer 后，项目内 reviewer 仍可完成审核。

修复要求：

1. 若 `review_requests.reviewer_id` 不为空，只有以下用户可完成：
   - 指定 reviewer；
   - admin；
   - 项目内 leader；
   - 项目内 teacher；
2. 项目内 reviewer 只有在未指定 reviewer，或自己就是指定 reviewer 时，才可完成；
3. 非项目成员不得完成；
4. 普通 member 不得审核他人输出。

### 5. 拦截提交者自审

当前提交者可以把自己设为 reviewer 后完成自审。

修复要求：

1. `ctx.submitter_id == 当前用户` 时，不得完成审核；
2. 例外：当前用户同时是 admin / 项目内 leader / 项目内 teacher；
3. 项目内 reviewer 身份本身不应允许自审；
4. 返回清晰权限错误。

### 6. 检查关键 UPDATE affected_rows

提交审核时必须检查：

1. `update_output_status(output_id, 'submitted')`;
2. `update_task_status(task_id, 'submitted')`;

完成审核时必须检查：

1. `update_review_request_status(request_id, review_status)`;
2. `update_output_status(output_id, review_status)`;
3. `update_task_status(task_id, review_status)`;

修复要求：

1. 任一 `affected_rows == 0` 必须 rollback；
2. 不得返回 success；
3. 返回清晰错误；
4. 不得出现审核记录写入成功但状态未更新的情况；
5. 不得出现状态更新失败但 `operation_logs` 成功提交的情况。

### 7. 建议补齐 issue-tags 认证

非阻塞但建议同步修复：

1. `GET /api/issue-tags` 也解析 `Authorization: Bearer token`；
2. 至少要求登录用户才能查询；
3. 保持 Stage-09 接口认证风格一致。

## 复审要求

修复完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-009-FIX-review-center.md`

handoff 必须说明：

1. 6 个阻塞问题分别如何修复；
2. 是否修改了允许范围之外的文件；
3. 是否仍未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
4. 是否仍未实现成果库、统计看板、Stage-10 内容；
5. 是否执行 Python 语法检查；
6. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/reviews.py app/services/review_service.py app/repositories/review_repo.py run.py
```

如修改了 `task_service.py` 或 `task_repo.py`，也请执行：

```bash
python3 -m py_compile app/services/task_service.py app/repositories/task_repo.py
```

