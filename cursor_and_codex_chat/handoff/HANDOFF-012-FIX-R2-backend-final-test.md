# HANDOFF-012-FIX-R2：Stage-12 文档修复版（第二轮）

## 任务状态

**完成**。

---

## 一、Codex 本轮唯一问题

`backend/scripts/test_report_material.md` 中创建任务示例仍使用错误字段：

- `task_name`（错误，应为 `title`）
- `task_type`（错误，应为 `task_type_id`）

而真实接口 `POST /api/projects/{project_id}/tasks` 需要的字段为 `task_type_id`、`title`、`description`、`assignee_id`、`priority`、`due_date`。

---

## 二、本次修改文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/scripts/test_report_material.md` | 修改 | 4 处 `task_name`/`task_type` 替换为 `task_type_id`/`title` |
| `cursor_and_codex_chat/handoff/HANDOFF-012-FIX-R2-backend-final-test.md` | 新建 | 本次交接文档 |

---

## 三、test_report_material.md 创建任务示例如何修复

共修复 4 处：

| 位置 | 修复前 | 修复后 |
|------|--------|--------|
| TC-017 测试用例 | `'{"task_name":"测试任务","task_type":"code_review"}'` | `'{"task_type_id":1,"title":"生成需求分析初稿","description":"为数据库课程报告生成需求分析部分","assignee_id":2,"priority":"normal","due_date":"2026-06-10 23:59:59"}'` |
| TC-018 列表返回字段 | `{task_id,task_name,...}` | `{task_id,title,...}` |
| 10.7 业务接口测试 | `'{"task_name":"需求分析任务","task_type":"document_writing"}'` | `'{"task_type_id":1,"title":"生成需求分析初稿","description":"为数据库课程报告生成需求分析部分","assignee_id":2,"priority":"normal","due_date":"2026-06-10 23:59:59"}'` |
| 10.7 业务接口测试（重复） | `'{"task_name":"需求分析","task_type":"document_writing"}'` | 同上 |

所有创建任务请求体现已与真实接口 `POST /api/projects/{project_id}/tasks` 的字段完全一致。

---

## 四、是否还存在 task_name / task_type 错误字段

**否**。

`backend/scripts/test_report_material.md` 中已不存在作为请求体字段的 `task_name` 或 `task_type`。剩余的 `task_type` 仅出现在合法路由路径 `/api/task-types` 中（查询任务类型列表），不属于字段名。

---

## 五、是否修改业务代码

**否**。本次仅修改 `backend/scripts/test_report_material.md` 的文档内容，未修改任何 `backend/app/` 下的业务代码。

---

## 六、是否修改 database

**否**。

---

## 七、是否修改 frontend

**否**。

---

## 八、是否实现 Stage-13

**否**。

---

## 九、当前环境限制说明

- 当前环境无 MySQL，无法执行真实的数据库连接和接口集成测试
- WSL2 环境无法直接访问 Windows 宿主机上的 MySQL
- 实际 MySQL 数据库导入和接口联调验证需在 Windows MySQL 可连接环境中补做
- 课程报告中的数据库截图和接口联调截图建议在 Windows 环境下完成
- 所有涉及数据库读写的接口测试均标注"待补充截图"或"待 Windows MySQL 环境验证"
