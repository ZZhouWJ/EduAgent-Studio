# REVIEW-009-FIX-R2 审核中心模块复审报告

## 1. 审查结论

**不通过。**

本轮只复审唯一剩余问题组：`_can_complete_review()` 权限逻辑是否收紧。当前代码仍保留上一轮失败逻辑：

- 指定 `reviewer_id` 后，项目内其他 `reviewer` 仍可越过指定 reviewer 完成审核；
- `is_self_submit` 已定义但未使用，项目内 reviewer 仍可能审核自己提交的输出；
- 请求中指定的 `cursor_and_codex_chat/handoff/HANDOFF-009-FIX-R2-review-center.md` 在远程项目中不存在，本轮实际读取了上一轮 `HANDOFF-009-FIX-review-center.md` 和当前代码。

因此：**不允许进入 Stage-10**，本次不发布 `TASK-010-artifact-library.md`。

## 2. 指定 reviewer_id 后权限是否已收紧

**未收紧到位。**

代码位置：`backend/app/services/review_service.py:438-444`

当前逻辑：

```python
if reviewer_id is not None:
    if reviewer_id == user_id:
        return True
    if _is_project_privileged(project_id, user_id):
        return True
    return False
```

问题在于 `_is_project_privileged()` 仍包含项目内 `reviewer`：

```python
leader OR teacher OR reviewer
```

因此当 `reviewer_id = A` 时，项目内 reviewer B 仍会因为 `_is_project_privileged()` 返回 True 而可以完成审核。

## 3. 项目内其他 reviewer 是否已不能越过指定 reviewer

**未修复。**

验收要求是：

- 指定 reviewer 本人可以；
- admin 可以；
- 项目内 leader 可以；
- 项目内 teacher 可以；
- 项目内其他 reviewer 不可以；
- 普通 member 不可以；
- 非项目成员不可以。

当前实现仍允许“项目内其他 reviewer”完成指定给别人的审核请求。

## 4. 自审拦截是否生效

**未生效。**

代码位置：`backend/app/services/review_service.py:431-448`

`is_self_submit = (submitter_id == user_id)` 已定义，但后续没有使用。未指定 `reviewer_id` 时，如果提交者本人同时是项目内 reviewer，会因为 `_is_project_privileged(project_id, user_id)` 返回 True 而通过审核权限判断。

## 5. 项目 reviewer 是否已不能自审

**未修复。**

当前逻辑没有在 `_can_complete_review()` 中对项目 reviewer 自审进行拦截。按要求：

- admin 自审可作为例外；
- 项目内 leader 自审可作为例外；
- 项目内 teacher 自审可作为例外；
- 项目 reviewer 不得审核自己提交的输出；
- 普通 member 不得审核自己提交的输出。

当前代码无法满足该规则。

## 6. 不得破坏已通过内容

静态复核结果：

- reviewer_id 提交校验逻辑仍存在；
- 普通 member 被指定 reviewer 后可通过 `OR r.reviewer_id = %s` 查看自己的 pending 请求；
- `review_status` 仍只允许 `approved / rejected / revision_required`；
- 关键状态更新的 affected_rows 检查仍存在；
- 提交审核和完成审核事务结构仍存在；
- 未在本轮审查对象中发现 `adopted_outputs` 写入；
- 未发现成果库、统计看板或 Stage-10 接口实现。

说明：远程 `git status` 显示历史上存在大量已修改文件，包括 `database/`、`docs/` 等，但本轮只针对 Stage-09 Fix R2 的剩余权限逻辑做窄口径复审，未据此扩大为全量变更审查。

## 7. 语法检查结果

已执行：

```bash
cd backend
python3 -m py_compile app/main.py app/routers/reviews.py app/services/review_service.py app/repositories/review_repo.py run.py
```

结果：**通过，输出 `PY_COMPILE_OK`。**

环境限制：

- 当前 Codex 环境无法直接访问 Windows MySQL；
- 本轮以静态代码审查和 Python 编译检查为准；
- 不因无法连接 MySQL 阻塞 Stage-09，但权限逻辑仍明显错误，因此判定不通过。

## 8. 是否发现越界修改

本轮窄口径复审未发现成果库、统计看板、Stage-10 或 `adopted_outputs` 越界实现。

但请求指定的 `HANDOFF-009-FIX-R2-review-center.md` 文件不存在，需要 Cursor 补齐或确认文件名。

## 9. 是否允许进入 Stage-10

**不允许。**

## 10. 剩余问题

只剩 `_can_complete_review()` 权限逻辑问题，需要 Cursor 按以下规则修复：

1. 指定 `reviewer_id` 不为空时：
   - admin 可以；
   - 指定 reviewer 本人可以；
   - 项目内 leader 可以；
   - 项目内 teacher 可以；
   - 项目内其他 reviewer 不可以；
   - 普通 member 不可以；
   - 非项目成员不可以。

2. `reviewer_id` 为空时：
   - admin 可以；
   - 项目内 leader 可以；
   - 项目内 teacher 可以；
   - 项目内 reviewer 可以；
   - 普通 member 不可以；
   - 非项目成员不可以。

3. 自审拦截：
   - `current_user_id == submitter_id` 时必须进入自审判断；
   - 例外只允许 admin、项目内 leader、项目内 teacher；
   - 项目 reviewer 不得审核自己提交的输出；
   - 普通 member 不得审核自己提交的输出；
   - `is_self_submit` 必须真正参与判断。

4. 建议拆分权限 helper：
   - `_is_project_leader_or_teacher(project_id, user_id)`；
   - `_is_project_reviewer(project_id, user_id)`；
   - 不要在指定 reviewer 场景使用包含 reviewer 的 `_is_project_privileged()`。

