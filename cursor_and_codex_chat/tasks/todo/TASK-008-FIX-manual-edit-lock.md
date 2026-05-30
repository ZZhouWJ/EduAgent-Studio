# TASK-008-FIX 人工编辑、批注与乐观锁模块修复任务

## 任务状态

已完成。

## 任务目标

根据 `cursor_and_codex_chat/reviews/REVIEW-008-manual-edit-lock.md` 修复 Stage-08 审查发现的阻塞问题。修复完成后提交 handoff，等待 Codex 复审。复审通过前不得进入 Stage-09。

## 允许修改文件

- `backend/app/routers/tasks.py`
- `backend/app/services/task_service.py`
- `backend/app/repositories/task_repo.py`
- `cursor_and_codex_chat/handoff/HANDOFF-008-FIX-manual-edit-lock.md`

## 禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现

1. 审核中心；
2. 成果库；
3. 统计看板；
4. 前端页面；
5. Stage-09 审核中心内容。

## 必须修复的问题

### 1. 补充 save-as-new-version 接口路径

当前只实现了：

- `POST /api/outputs/{output_id}/save-as`

本轮验收要求必须实现：

- `POST /api/outputs/{output_id}/save-as-new-version`

修复要求：

1. 增加 `POST /api/outputs/{output_id}/save-as-new-version`；
2. 可保留 `/save-as` 兼容路径；
3. 两个路径如共存，必须调用同一个 service 函数；
4. 不得改变另存为新版本的事务、权限、`parent_output_id`、`version_no` 逻辑。

### 2. 校验 comment_type 枚举

Schema 中 `output_comments.comment_type` 只允许：

- `comment`
- `suggestion`
- `approval`

当前只校验非空。

修复要求：

1. 增加 `VALID_COMMENT_TYPE` 或等价校验；
2. 非法 `comment_type` 应返回统一参数错误；
3. 不得把非法值交给数据库层报错；
4. 不得新增 Schema 未定义的批注类型。

### 3. 修复批注状态更新的项目内 leader 权限

当前批注状态更新检查全局角色 `"project_leader"`，但项目成员表中的项目负责人角色是：

- `project_members.project_role = 'leader'`

修复要求：

1. 批注状态更新应允许 admin；
2. 应允许批注创建人；
3. 应允许项目内 `leader`；
4. 应允许项目内 `teacher`；
5. 普通 member 不应仅因项目成员身份更新他人批注状态；
6. 非项目成员仍不得更新；
7. 建议复用 `project_repo.is_user_project_leader(project_id, user_id)`，并补充或复用项目内 teacher 判断。

## 建议补充

非阻塞但建议同步修复：

- 新增批注时写入 `created_by`；
- 更新批注状态时写入 `updated_by`；
- handoff 中说明 `/save-as` 是否保留为兼容路径。

## 复审要求

修复完成后请创建：

- `cursor_and_codex_chat/handoff/HANDOFF-008-FIX-manual-edit-lock.md`

handoff 必须说明：

1. 3 个阻塞问题分别如何修复；
2. 是否修改了允许范围之外的文件；
3. 是否仍未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
4. 是否执行 Python 语法检查；
5. 如无法连接 Windows MySQL，请明确说明。

## 建议检查命令

```bash
cd backend
python3 -m py_compile app/main.py app/routers/tasks.py app/services/task_service.py app/repositories/task_repo.py run.py
```

