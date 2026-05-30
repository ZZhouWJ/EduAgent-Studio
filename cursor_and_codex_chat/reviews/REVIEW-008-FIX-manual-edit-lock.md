# REVIEW-008-FIX 人工编辑、批注与乐观锁模块修复复审报告

## 1. 审查结论

**通过。**

本轮只复审 `REVIEW-008-manual-edit-lock.md` 中指出的 3 个阻塞问题。三项均已修复，未发现新的阻塞问题，未发现越界实现。**允许进入 Stage-09**。

已发布：

- `cursor_and_codex_chat/tasks/todo/TASK-009-review-center.md`

## 2. 3 个阻塞问题是否全部修复

结论：**已全部修复。**

### 2.1 save-as-new-version 路径是否补齐

结论：**已修复。**

检查结果：

- 已存在 `POST /api/outputs/{output_id}/save-as-new-version`；
- `/save-as-new-version` 与保留的 `/save-as` 兼容路径共用 `_save_as_impl()`；
- `_save_as_impl()` 调用同一个 `task_service.save_output_as_new_version()`；
- 未发现重复写两套业务逻辑；
- 原另存逻辑仍返回新 `output_id` 和 `version_no`。

### 2.2 comment_type 枚举校验是否正确

结论：**已修复。**

检查结果：

- `task_repo.py` 定义 `VALID_COMMENT_TYPE = {"comment", "suggestion", "approval"}`；
- `create_output_comment()` 在 service 层校验 `comment_type`；
- 非法值会抛出 `ValidationException`，不会进入数据库写入；
- repository 只接收 service 校验后的合法 `comment_type`；
- 未修改数据库结构。

### 2.3 批注状态更新权限是否正确识别项目内 leader

结论：**已修复。**

检查结果：

- `update_comment_status()` 先通过 `get_comment_project_context(comment_id)` 获取 `output_id`、`task_id`、`project_id`；
- 非项目成员会被 `_can_access_project(project_id, user_id)` 拦截；
- admin 仍可操作；
- 批注创建人可操作自己的批注；
- 项目内 `leader` 使用 `project_repo.is_user_project_leader(project_id, user_id)` 判断；
- 项目内 `teacher` 使用 `project_repo.is_user_project_teacher(project_id, user_id)` 判断；
- 项目内 `reviewer` 使用 `project_repo.is_user_project_reviewer(project_id, user_id)` 判断；
- 普通 member 不能随意更新他人批注状态；
- 未发现跨项目更新批注状态风险。

## 3. 是否发现新问题

未发现新的阻塞问题。

说明：

- 本轮仅复审上轮 3 个阻塞问题；
- 未进行 Stage-08 全量重新审查；
- 未连接 Windows MySQL 做真实接口联调。

## 4. 是否发现越界修改

未发现。

- 未发现本轮修改 `database/`；
- 未发现本轮修改 `frontend/`；
- 未发现本轮修改 `docs/`；
- 未发现审核中心、成果库、统计看板或 Stage-09 内容实现。

## 5. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py app/repositories/project_repo.py run.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态审查和 Python 编译检查为准，不因无法连接 MySQL 阻塞。

## 6. 是否允许进入 Stage-09

**允许。**

已发布：

- `cursor_and_codex_chat/tasks/todo/TASK-009-review-center.md`

