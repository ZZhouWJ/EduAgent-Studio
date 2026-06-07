# HANDOFF-017-FIX-R2：修复 backend/scripts/route_list.md 中的 /save-as 旧接口

**阶段**：Stage-17 FIX R2（仅修复一个阻塞点）
**执行人**：Cursor 收尾工程师
**日期**：2026-06-01
**状态**：已完成

---

## 一、Codex 本轮唯一阻塞点

`backend/scripts/route_list.md` 第 93 行将以下两个接口都列为正式接口：

- `POST /api/outputs/{output_id}/save-as`（旧/兼容路径）
- `POST /api/outputs/{output_id}/save-as-new-version`（验收指定路径）

但 `/save-as` 不能作为正式验收接口，只能作为旧接口反面说明。

---

## 二、修改文件

| 文件路径 | 修改内容 |
|----------|----------|
| `backend/scripts/route_list.md` | 删除第 93 行的 `POST /api/outputs/{output_id}/save-as`，仅保留 `POST /api/outputs/{output_id}/save-as-new-version`，功能说明改为"将当前输出另存为新版本" |

---

## 三、是否已将 /save-as 正式接口改为 /save-as-new-version

**是**。`backend/scripts/route_list.md` 中的正式接口已统一为：

```
POST /api/outputs/{output_id}/save-as-new-version
```

功能说明：**将当前输出另存为新版本**。

`POST /api/outputs/{output_id}/save-as` 已从正式接口清单中删除。

---

## 四、是否修改后端业务代码

**答案：否**。本次仅修改了 `backend/scripts/route_list.md` 文档文件，未修改 `backend/app/` 下任何业务代码。

---

## 五、是否修改前端业务代码

**答案：否**。本次未修改 `frontend/src/` 下任何文件。

---

## 六、是否修改数据库

**答案：否**。本次未修改 `database/` 下任何文件。

---

## 七、是否进入新阶段

**答案：否**。本次仅修复一个文档阻塞点，不进入任何新阶段。

---

## 八、当前环境限制说明

| 限制项 | 说明 |
|--------|------|
| 远程环境无 Node | 无法执行 `npm install` / `npm run build` |
| WSL2 无法访问 Windows MySQL | 涉及数据库读写的接口测试无法在远程环境验证 |
| MySQL 未初始化 | `database/01-07` 未执行 |

---

*本文件为 Stage-17 FIX R2 阶段交接文档，供 Codex 最终复审使用。*
