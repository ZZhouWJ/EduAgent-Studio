# REVIEW-009-FIX 审核中心模块修复复审报告

## 1. 审查结论

**不通过。**

本轮只复审 `REVIEW-009-review-center.md` 中指出的 6 个阻塞问题。当前已有 4 个问题修复到位，但完成审核权限仍存在 2 个关键问题：指定 reviewer 后项目内 reviewer 仍可越过指定 reviewer；提交者自审拦截变量已定义但未生效。

因此：**暂不允许进入 Stage-10**，本次不发布 `TASK-010-artifact-library.md`。

## 2. 6 个阻塞问题是否全部修复

结论：**未全部修复。**

### 2.1 提交审核 reviewer_id 校验

结论：**已修复。**

检查结果：

- `reviewer_id` 为空时允许提交；
- `reviewer_id` 不为空时会查询用户是否存在且未删除；
- 会拒绝 `reviewer_id == 当前用户`；
- reviewer 必须是 admin 或当前项目成员；
- 校验发生在插入 `review_requests` 之前。

### 2.2 普通 member 被指定 reviewer 后能否看到待审核请求

结论：**已修复。**

检查结果：

- admin 可查看全部；
- 项目内 `leader` / `teacher` / `reviewer` 可查看本项目 pending；
- 非 admin 查询增加了 `OR r.reviewer_id = 当前用户`；
- 普通 member 若被指定为 reviewer，可查看分配给自己的 pending；
- `project_id` 过滤仍会生效；
- 未发现跨项目泄露风险。

### 2.3 完成审核 review_status 白名单

结论：**已修复。**

检查结果：

- 已新增 `VALID_COMPLETE_REVIEW_STATUS = {"approved", "rejected", "revision_required"}`；
- `complete_review()` 使用该白名单；
- `pending`、`submitted`、`adopted`、`archived` 等非法状态会被拒绝并返回参数错误。

### 2.4 指定 reviewer 后权限是否收紧

结论：**未修复。**

问题：

- `backend/app/services/review_service.py:53-59` 的 `_is_project_privileged()` 包含项目内 `reviewer`；
- `backend/app/services/review_service.py:438-444` 在 `reviewer_id` 不为空时，仍调用 `_is_project_privileged(project_id, user_id)`；
- 因此在已指定 reviewer 的审核请求中，其他项目内 reviewer 仍可越过指定 reviewer 完成审核。

这与复审要求冲突：当 `review_requests.reviewer_id` 不为空时，只允许指定 reviewer 本人、admin、项目 leader、项目 teacher 完成审核，项目 reviewer 不应绕过指定 reviewer。

### 2.5 自审是否被拦截

结论：**未修复。**

问题：

- `backend/app/services/review_service.py:431-433` 定义了 `is_self_submit = (submitter_id == user_id)`；
- 但后续权限判断没有使用 `is_self_submit`；
- 在未指定 reviewer 的场景中，如果提交者同时是项目内 reviewer，`_is_project_privileged()` 会返回 True，提交者仍可审核自己提交的输出；
- 按要求，提交者自审只应允许 admin、项目 leader、项目 teacher，普通 reviewer 不得审核自己提交的输出。

说明：提交审核阶段已经拒绝 `reviewer_id == 当前用户`，但这不能覆盖“未指定 reviewer 时提交者作为项目 reviewer 自审”的场景。

### 2.6 关键状态更新 affected_rows 检查

结论：**已修复。**

检查结果：

- 提交审核时检查 `task_outputs.status = submitted` 更新结果；
- 提交审核时检查 `project_tasks.status = submitted` 更新结果；
- 完成审核时检查 `review_requests.request_status` 更新结果；
- 完成审核时检查 `task_outputs.status` 更新结果；
- 完成审核时检查 `project_tasks.status` 更新结果；
- 任一 `affected_rows == 0` 会 rollback 并抛出清晰错误。

## 3. 是否发现新问题

未发现新的代码阻塞问题。

说明：

- 本轮重点只复审上轮 6 个阻塞问题；
- 未进行 Stage-09 全量重新审查；
- 未连接 Windows MySQL 做真实接口联调。

## 4. 是否发现越界修改

未发现。

- 未发现本轮修改 `database/`；
- 未发现本轮修改 `frontend/`；
- 未发现本轮修改 `docs/`；
- 未发现成果库、统计看板或 Stage-10 内容；
- 未发现写入 `adopted_outputs`。

## 5. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/reviews.py app/services/review_service.py app/repositories/review_repo.py run.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准，不因无法连接 MySQL 阻塞。

## 6. 是否允许进入 Stage-10

**不允许。**

## 7. 必须修复的问题

唯一剩余问题组：`_can_complete_review()` 权限逻辑仍需修正。

具体要求：

1. 当 `review_requests.reviewer_id` 不为空时：
   - 允许 admin；
   - 允许指定 reviewer 本人；
   - 允许项目内 leader；
   - 允许项目内 teacher；
   - 不允许其他项目内 reviewer 越过指定 reviewer；
   - 不允许普通 member；
   - 不允许非项目成员。

2. 当 `review_requests.reviewer_id` 为空时：
   - 允许 admin；
   - 允许项目内 leader；
   - 允许项目内 teacher；
   - 允许项目内 reviewer；
   - 普通 member 不允许。

3. 自审拦截：
   - 如果 `current_user_id == submitter_id`，必须拒绝；
   - 例外只允许 admin、项目内 leader、项目内 teacher；
   - 项目内 reviewer 不得审核自己提交的输出。

建议实现：

- 不要在指定 reviewer 场景直接调用包含 reviewer 的 `_is_project_privileged()`；
- 可拆分 helper：
  - `_is_project_leader_or_teacher(project_id, user_id)`;
  - `_is_project_reviewer(project_id, user_id)`;
- 先处理 admin；
- 再处理自审例外；
- 再根据 reviewer_id 是否为空分别判断。

