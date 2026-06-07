# HANDOFF-009-FIX-R2：Stage-09 审核中心模块第二次修复版

## 任务状态

**完成** — `_can_complete_review()` 权限逻辑已修正，`is_self_submit` 真正参与判断。

---

## 一、本轮 Codex 未通过原因

| 问题 | 说明 |
|---|---|
| `_is_project_privileged()` 被用于完成审核权限判断 | `_is_project_privileged()` 包含 reviewer，导致指定 reviewer 场景下项目内其他 reviewer 可越权完成审核 |
| `is_self_submit` 定义但未参与判断 | 自审拦截逻辑未真正生效 |
| `HANDOFF-009-FIX-R2-review-center.md` 不存在 | 上一轮未创建本轮 handoff 文件 |

---

## 二、本次修改文件

| 文件 | 修改内容 |
| --- | --- |
| `backend/app/services/review_service.py` | 移除 `_is_project_privileged()`；新增 `_get_project_role()`；重写 `_can_complete_review()`；`get_review_detail` 改用个体角色判断 |
| `cursor_and_codex_chat/handoff/HANDOFF-009-FIX-R2-review-center.md` | 新建 |

---

## 三、`_can_complete_review()` 最终权限规则

### 核心逻辑结构

```python
def _can_complete_review(user, user_id, ctx, project_id) -> bool:
    # 1. admin 永远允许
    if _is_admin(user):
        return True

    # 2. 获取当前用户在该项目内的 project_role
    project_role = _get_project_role(project_id, user_id)
    # project_role 来自 project_members.project_role

    is_project_leader   = (project_role == "leader")
    is_project_teacher  = (project_role == "teacher")
    is_project_reviewer = (project_role == "reviewer")
    is_project_member   = project_role in ("leader", "teacher", "reviewer", "member")

    is_assigned_reviewer = (reviewer_id is not None and reviewer_id == user_id)
    is_self_submit       = (submitter_id == user_id)

    # 3. 非项目成员，且不是指定 reviewer：不允许
    if not is_project_member and not is_assigned_reviewer:
        return False

    # 4. 自审拦截（is_self_submit 真正参与判断）
    if is_self_submit:
        return is_project_leader or is_project_teacher

    # 5. reviewer_id 不为空：指定审核人场景
    if reviewer_id is not None:
        return is_assigned_reviewer or is_project_leader or is_project_teacher

    # 6. reviewer_id 为空：未指定审核人场景
    return is_project_leader or is_project_teacher or is_project_reviewer
```

### 关键变更

- **`_is_project_privileged()` 已移除**：不再使用包含 reviewer 的联合函数
- **`is_self_submit` 真正参与判断**：第 4 步自审拦截返回 `is_project_leader or is_project_teacher`，项目 reviewer 和普通 member 无法自审
- **个体角色布尔值**：`is_project_leader`、`is_project_teacher`、`is_project_reviewer` 分别判断
- **project_role 来源**：`review_repo.get_project_member_role(project_id, user_id)`，来自 `project_members.project_role`

---

## 四、reviewer_id 不为空时（指定审核人场景）

| 角色 | 是否允许完成审核 |
|---|---|
| admin | 允许 |
| 指定 reviewer（本人）| 允许 |
| 项目 leader | 允许 |
| 项目 teacher | 允许 |
| 项目内其他 reviewer | **不允许** |
| 普通 member | **不允许** |
| 非项目成员 | **不允许** |

---

## 五、reviewer_id 为空时（未指定审核人场景）

| 角色 | 是否允许完成审核 |
|---|---|
| admin | 允许 |
| 项目 leader | 允许 |
| 项目 teacher | 允许 |
| 项目 reviewer | 允许 |
| 普通 member | **不允许** |
| 非项目成员 | **不允许** |

---

## 六、自审规则

当 `submitter_id == current_user_id` 时（自审）：

| 角色 | 是否允许 |
|---|---|
| admin | 允许（第一步已 return True）|
| 项目 leader | 允许 |
| 项目 teacher | 允许 |
| 项目 reviewer | **不允许** |
| 普通 member | **不允许** |

---

## 七、是否仍使用包含 reviewer 的 `_is_project_privileged()` 判断完成审核权限

**否**。`_is_project_privileged()` 已完全移除。

完成审核权限判断中，仅在第 3 步"非项目成员检查"中使用 `is_project_member`（`project_role in ("leader","teacher","reviewer","member")`），在第 5 步和第 6 步使用个体布尔值 `is_project_leader`、`is_project_teacher`、`is_project_reviewer`，不含 reviewer 的联合判断。

---

## 八、是否实现成果库

**否**。

---

## 九、是否写入 adopted_outputs

**否**。

---

## 十、是否修改 database

**否**。

---

## 十一、Python 语法检查命令

```bash
cd backend
python -m py_compile app/services/review_service.py
```

结果：`EXIT:0`（通过）。

---

## 十二、需要 Codex 复审的重点

1. `_is_project_privileged()` 是否已完全从 `review_service.py` 中移除
2. `_can_complete_review()` 中 `is_self_submit` 是否真正参与判断（不是只定义不调用）
3. 指定 reviewer 场景下（`reviewer_id is not None`），项目内普通 reviewer 是否返回 False
4. 自审场景下（`is_self_submit = True`），项目 reviewer 是否返回 False
5. `project_role` 是否来自 `project_members.project_role`，而非全局角色字符串
6. `get_review_detail` 中的权限判断是否也已修正（不依赖已移除的函数）
7. `HANDOFF-009-FIX-R2-review-center.md` 是否已创建

---

## 十三、验收清单

- [x] `_is_project_privileged()` 已从 `review_service.py` 移除
- [x] `_get_project_role()` 已新增（调用 `review_repo.get_project_member_role`）
- [x] `_can_complete_review()` 使用个体角色布尔值判断
- [x] `is_self_submit` 真正参与自审拦截判断
- [x] 指定 reviewer 场景：项目内其他 reviewer/member 不能越权
- [x] 自审场景：项目 reviewer/member 不能自审
- [x] `get_review_detail` 权限判断已同步修正
- [x] Python 语法检查通过
- [x] `HANDOFF-009-FIX-R2-review-center.md` 已创建

---

**本修复完成后停止，等待 Codex 复审。**
