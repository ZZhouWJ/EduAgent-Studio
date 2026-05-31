# HANDOFF-010-FIX-R2：Stage-10 成果库与分支合并模块第二次修复版

## 任务状态

**完成** — Stage-10 Fix R2 唯一剩余问题已修复。

---

## 一、Codex 本轮唯一剩余问题

`manual_merge` 中将 `target_branch_id` 更新为 `active` 时，未检查 `affected_rows`：

```python
# 修复前（问题代码）
artifact_repo.update_branch_status(target_branch_id, "active", conn)
# ↑ 没有接收返回值，没有检查 affected_rows
```

若目标分支不存在或已被删除，merge_records 仍会写入并提交，导致数据不一致。

---

## 二、修改文件

| 文件 | 修改内容 |
| --- | --- |
| `backend/app/services/artifact_service.py` | manual_merge 中 target_branch → active 增加 affected_rows 检查 |
| `cursor_and_codex_chat/handoff/HANDOFF-010-FIX-R2-artifact-library.md` | 新建 |

---

## 三、target_branch_id -> active 的 affected_rows 如何检查

**修复后**：

```python
# manual_merge: 创建新 output
elif merge_strategy == "manual_merge":
    merged_output_id = artifact_repo.create_task_output(...)
    # 1. 更新 source_branch → merged（已有检查）
    affected = artifact_repo.update_branch_status(source_branch_id, "merged", conn)
    if affected == 0:
        conn.rollback()
        raise NotFoundException(message="源分支不存在或无权更新状态")
    # 2. 更新 target_branch → active（新增检查）
    affected = artifact_repo.update_branch_status(target_branch_id, "active", conn)
    if affected == 0:
        conn.rollback()
        raise NotFoundException(message="目标分支不存在或无权更新状态")
```

- `update_branch_status` 返回 `affected_rows`（已由 repository 层实现）
- service 层接收返回值
- `affected == 0` 时立即 `rollback`，抛出 `NotFoundException`

---

## 四、affected_rows = 0 时如何处理

- 调用 `conn.rollback()` 回滚整个事务
- 抛出 `NotFoundException(message="目标分支不存在或无权更新状态")`
- 不继续执行后续 merge_records 和 operation_logs 写入
- 不返回 success

---

## 五、四种策略分支状态 affected_rows 检查完整汇总

| 策略 | 分支 | 状态 | affected_rows 检查 |
|---|---|---|---|
| `adopt_source` | source_branch | merged | ✓ |
| `adopt_target` | target_branch | merged | ✓ |
| `manual_merge` | source_branch | merged | ✓ |
| `manual_merge` | target_branch | active | **✓（本次新增）** |
| `adopt_separately` | source_branch | merged | ✓ |

---

## 六、是否修改 database

**否**。

---

## 七、是否修改 frontend

**否**。

---

## 八、是否实现统计看板

**否**。

---

## 九、Python 语法检查命令

```bash
cd backend
python -m py_compile app/services/artifact_service.py
```

结果：`EXIT:0`（通过）。

---

## 十、当前环境限制

- 当前环境无 MySQL，无法真实执行验证，基于静态代码审查。

---

## 十一、需要 Codex 复审的重点

1. manual_merge 中 target_branch → active 是否已接收 affected_rows 返回值
2. affected == 0 时是否立即 rollback 并抛出异常
3. 是否不吞掉异常、不返回 success
4. source_branch → merged 的检查是否保持完好
5. merge_records、operation_logs 是否仍在所有检查通过后执行

---

## 十二、验收清单

- [x] manual_merge 中 target_branch → active 已检查 affected_rows
- [x] affected == 0 时 rollback 并抛出 NotFoundException
- [x] 其他分支状态检查未被破坏
- [x] Python 语法检查通过
- [x] 未修改 database/frontend/docs

---

**本修复完成后停止，等待 Codex 复审。**
