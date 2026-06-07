# HANDOFF-DOC-frontend-template-sync-FIX：文档复审修复

## 任务状态

**完成**。

---

## 一、Codex 文档复审未通过原因

1. `docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md` 的 10.3 SQL 中使用了 `i.is_deleted = 0`，但 `ai_invocations` 表没有 `is_deleted` 字段
2. `docs/project_development_doc.md` 为 0 字节空文件，容易与正式文档混淆
3. 文档其他章节已在上一轮修复，本次复审重点检查以上两项

---

## 二、本次修改文件

| 文件 | 修改内容 |
|------|----------|
| `docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md` | 修复 10.3 SQL，移除错误的 `i.is_deleted` 条件 |
| `docs/project_development_doc.md` | 写入跳转说明（180 字节），指向正式文档 |

---

## 三、10.3 SQL 修复说明

**修复前：**
```sql
WHERE i.is_deleted = 0
-- 错误：ai_invocations 表没有 is_deleted 字段
```

**修复后：**
```sql
FROM ai_invocations i
JOIN ai_models m ON i.model_id = m.model_id
JOIN project_tasks t ON i.task_id = t.task_id AND t.is_deleted = 0
JOIN projects p ON t.project_id = p.project_id AND p.is_deleted = 0
GROUP BY m.display_name
ORDER BY call_count DESC;
```

修改要点：
- 通过 JOIN `project_tasks` 和 `projects` 过滤已删除数据（t.is_deleted = 0, p.is_deleted = 0）
- 不在 `ai_invocations` 上使用 is_deleted 条件
- 新增 `failed_count` 列统计失败调用
- 使用 `COALESCE` 处理 NULL token 值
- `COUNT(*)` 改为 `COUNT(i.invocation_id)` 提高准确性

---

## 四、project_development_doc.md 处理说明

**处理方式：方案 B（写入跳转说明）**

文件已写入：
```markdown
# 项目开发文档说明

本文件为早期占位文件，正式项目开发文档请查看：

docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md
```

选择方案 B 而非方案 A（删除）的原因：不确定是否有其他文件或目录结构强依赖该文件路径，写入跳转说明更为安全。

---

## 五、2.5 / 2.6 / 8.1 / 8.4 / 9.1 / 11.4 同步状态

以下章节在上一轮（再上一轮对话）中已修复，本次确认仍正确：

| 章节 | 状态 |
|------|------|
| 2.5 借鉴边界与合规说明 | ✅ 已改为"基于 V3 Admin Vite 模板"，含 8 条合规原则 |
| 2.6 基于 Vue3 开源后台模板的前端实现方案 | ✅ 标题已改，含方案表格、合规说明、参考定位表 |
| 8.1 推荐技术路线 | ✅ 已改为"前端：基于 V3 Admin Vite 二次开发" |
| 8.4 前端目录结构建议 | ✅ 已改为 V3 Admin Vite 裁剪后实际结构 |
| 9.1 整体界面风格 | ✅ 已改为"V3 Admin Vite 二次设计"，含 Mock 移除说明 |
| 11.4 第四阶段：前端开发 | ✅ 已改为"基于 V3 Admin Vite 模板裁剪改造" |

本次未重复修改以上章节。

---

## 六、其他旧表述修复状态

| 问题 | 状态 | 说明 |
|------|------|------|
| "用户注册" | ✅ 已在上一轮修复 | 5.2 改为具体接口清单 + 不开放注册说明 |
| "审核通过并采用事务" | ✅ 已在上一轮修复 | 拆分为"7.4 审核完成事务"和"7.5 成果采用事务" |
| "rr.status" | ✅ 已是 request_status | 10.2 SQL 正确使用 `rr.request_status` |
| "code: 200" | ✅ 全文无此表述 | 统一返回格式为 `{code:0,...}` |
| "task_name / task_type" | ✅ 全文无此表述 | 创建任务使用 task_type_id、title 等字段 |

---

## 七、是否修改代码

**否**。本次只修改文档。

---

## 八、是否修改数据库

**否**。

---

## 九、是否进入 Stage-14

**否**。

---

## 十、需要 Codex 复审的重点

1. 10.3 SQL 中 `ai_invocations` 不再使用 `is_deleted` 条件，改为通过 JOIN 过滤已删除项目/任务
2. `project_development_doc.md` 不再为 0 字节，已写入跳转说明
3. 文档中无"用户注册"、"rr.status"、"code: 200" 等与实际实现冲突的旧表述
4. 2.5/2.6/8.1/8.4/9.1/11.4 已同步为 V3 Admin Vite 二次开发口径
