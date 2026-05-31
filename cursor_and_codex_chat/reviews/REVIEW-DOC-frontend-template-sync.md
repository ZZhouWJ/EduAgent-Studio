# REVIEW-DOC: 前端模板方案同步文档复审报告

## 1. 审查结论

**需要继续修改**

项目开发文档主体已经从旧的“Vue3 自主实现 / 只参考 UI 风格”同步为当前实际方案：前端基于 **V3 Admin Vite** 成熟 Vue3 开源后台模板二次开发，并保留 `LICENSE` / `NOTICE.md` / 来源说明，移除模板 Mock API 与无关页面。

但本轮仍发现两个需要修复的问题：

1. `docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md` 的 **10.3 查询模型调用统计** 仍使用 `WHERE i.is_deleted = 0`，而 `ai_invocations` 表在当前数据库 Schema 中是审计表，不包含 `is_deleted` 字段。这是新的文档与数据库结构不一致问题。
2. `docs/project_development_doc.md` 存在但为 0 字节空文件，容易与真正的整合修订版项目开发文档混淆。建议删除、补充跳转说明，或同步为正式文档副本。

因此本轮文档复审暂不判定通过。

## 2. 2.5 是否已修正

**基本已修正，但建议补充完整参考项目列表。**

已确认 2.5 明确区分：

- 产品设计层面参考 LiteLLM、Dify、Langfuse、Helicone、Open WebUI、LobeChat 等项目；
- 前端工程实现层面基于 V3 Admin Vite 二次开发；
- 保留原模板 LICENSE 与来源说明；
- 不使用原模板 Logo、品牌名和无关业务页面；
- 删除或隐藏模板 Mock 数据和演示页面；
- 不复制 LobeChat / Open WebUI 的 React、Next.js、SvelteKit 源码；
- 不再笼统写“完全不直接复制源码”而与 V3 Admin Vite 模板使用冲突。

小问题：2.4 已单独介绍 One API 和 New API，但 2.5 总结句未显式列出 One API、New API。建议将 2.5 第一段补成“LiteLLM、One API、New API、Dify、Langfuse、Helicone、Open WebUI、LobeChat 等”。

## 3. 2.6 是否已修正

**已修正。**

2.6 标题已改为“基于 Vue3 开源后台模板的前端实现方案”，并明确：

- LobeChat / Open WebUI 只作为 AI 产品交互设计参考；
- 实际采用 V3 Admin Vite 作为 Vue3 前端模板底座；
- 技术栈为 Vue3 + Vite + TypeScript + Element Plus + Pinia + Vue Router；
- 提供 V3 Admin Vite GitHub 链接；
- 说明 MIT License；
- 说明保留 `frontend/LICENSE`、`frontend/NOTICE.md`；
- 说明 `.env.production` / `.env.staging` 已移除 Apifox Mock API；
- 删除了“Vue3 重新实现相似页面”“自主实现 Vue3 页面比改造源码更稳”等旧表述。

## 4. 8.1 是否已修正

**已修正。**

8.1 已将推荐技术路线改为：

- 前端：基于 V3 Admin Vite 开源模板二次开发；
- 后端：FastAPI；
- 数据库：MySQL 或 SQL Server；
- 数据库访问：参数化 SQL / Repository 层；
- 大模型接口：Mock ModelAdapter + 可选真实模型 API。

同时明确“不改造 LobeChat / Open WebUI 源码，但前端基础工程采用 V3 Admin Vite 开源 Vue3 后台模板进行二次开发”。未再出现“本项目应使用 Vue3 自主开发前端页面，而不是改造上述项目源码”的旧方案。

## 5. 8.4 是否已修正

**已修正。**

8.4 已改为 V3 Admin Vite 裁剪改造后的结构，包含：

- `package.json`
- `vite.config.ts`
- `index.html`
- `.env.example`
- `.env.production`
- `.env.staging`
- `LICENSE`
- `NOTICE.md`
- `README.md`
- `src/http/axios.ts`
- `src/layouts`
- `src/pages`
- `src/pinia`
- `src/router`
- `src/plugins`
- `src/common`

并说明具体目录以 V3 Admin Vite 模板裁剪后的实际结构为准，课程报告重点说明品牌替换、认证接口适配、菜单重构、Mock API 清理和业务占位页设计。

## 6. 9.1 是否已修正

**已修正。**

9.1 已明确：

- 界面基于 V3 Admin Vite 成熟后台管理风格进行二次设计；
- 使用左侧导航栏、顶部用户信息栏、卡片式内容区、状态标签、表格容器和统一主题色；
- 视觉参考 New API、LobeChat、Open WebUI 等 AI 平台产品质感；
- 不复用 LobeChat / Open WebUI 源码和品牌素材；
- 原模板 Mock API、Mock 数据和示例业务页面已移除或禁用。

## 7. 11.4 是否已修正

**已修正。**

11.4 已从普通“搭建前端项目”改为“基于 V3 Admin Vite 开源模板裁剪并改造前端项目”，并包含：

- 引入并裁剪 V3 Admin Vite 模板；
- 保留 LICENSE / NOTICE 与来源说明；
- 替换系统品牌和菜单；
- 移除模板 Mock API、Mock 数据和无关演示页面；
- 适配后端登录接口；
- 实现路由守卫与用户状态；
- 实现后台整体布局；
- 仅实现占位页面，后续逐步接入真实业务接口。

## 8. 旧问题是否已修正

**大部分已修正。**

已确认：

1. **用户注册**：5.2 不再写用户注册为已实现功能，已改为用户登录、用户信息查询、退出登录、密码哈希存储、角色分配、权限控制、登录日志记录，并注明“不开放用户自主注册功能”。
2. **adopted_outputs**：7.4 审核完成只更新 `approved` 状态并写审核记录；7.5 成果采用阶段才写入 `adopted_outputs`。这与 Stage-09 / Stage-10 边界一致。
3. **rr.status**：10.2 已使用 `rr.request_status`，WHERE 条件为 `rr.request_status = 'pending'`。
4. **/api/auth/register**：未发现作为当前已实现接口出现。
5. **code: 200**：未发现继续作为统一返回格式出现。
6. **task_name / task_type**：未发现继续作为创建任务请求字段出现；文档中出现的是合法字段 `task_type_id` 或表名 `task_types`。

## 9. 是否仍存在与 V3 Admin Vite 二次开发方案冲突的表述

**未发现核心冲突表述。**

全文未发现仍与当前方案冲突的：

- “自主实现前端页面”
- “设计复刻，不做源码迁移”
- “Vue3 重新实现相似页面”
- “本项目应使用 Vue3 自主开发前端页面，而不是改造上述项目源码”

文档中保留的“不迁移 LobeChat / Open WebUI 源码”属于正确语境：对 LobeChat / Open WebUI 只参考设计；对 V3 Admin Vite 则允许并已基于开源模板代码二次开发。

## 10. 是否发现新的文档与代码不一致问题

**发现 1 个必须修复问题。**

### P0. 10.3 查询模型调用统计仍引用不存在字段 `ai_invocations.is_deleted`

位置：

- `docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md`
- 10.3 查询模型调用统计

当前 SQL：

```sql
FROM ai_invocations i
JOIN ai_models m ON i.model_id = m.model_id
WHERE i.is_deleted = 0
GROUP BY m.display_name
```

问题：

- 当前 `database/02_create_tables.sql` 中 `ai_invocations` 明确为“审计表，不做业务删除”；
- `ai_invocations` 表没有 `is_deleted` 字段；
- 这个问题曾在 Stage-11 统计模块中修复过，文档不应重新出现该字段。

修复建议：

```sql
FROM ai_invocations i
JOIN ai_models m ON i.model_id = m.model_id
JOIN projects p ON i.project_id = p.project_id
WHERE p.is_deleted = 0
GROUP BY m.display_name
```

如需进一步过滤任务，可关联 `project_tasks` 并过滤 `project_tasks.is_deleted = 0`，但不得引用 `i.is_deleted`。

### P1. `docs/project_development_doc.md` 为空文件

该文件存在但为 0 字节。由于用户明确要求审查“如存在 docs/project_development_doc.md 或类似项目开发文档文件”，空文件容易造成误读。

建议：

1. 删除该空文件；或
2. 写入“正式项目开发文档见 `docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md`”；或
3. 将整合修订版内容同步到该文件。

## 11. 开源合规说明是否充分

**充分。**

已确认：

- `frontend/README.md` 说明 V3 Admin Vite 原项目链接；
- `frontend/NOTICE.md` 说明来源、作者、许可证和修改内容；
- `frontend/LICENSE` 保留 MIT License；
- 文档没有把模板包装成完全原创；
- 文档说明不使用原模板 Logo、品牌和 Mock 数据作为真实业务；
- 未发现将合规复用错误描述为“抄袭”或“不合规复用”。

## 12. 必须继续修改的问题

1. 修正项目开发文档 10.3 查询模型调用统计 SQL，删除 `WHERE i.is_deleted = 0`，改为通过现有字段和关联表过滤有效项目 / 任务。
2. 处理 `docs/project_development_doc.md` 0 字节空文件，避免与正式项目开发文档混淆。
3. 建议补充 2.5 第一段，将 One API、New API 显式列入产品设计参考项目清单。

## 13. 总结

前端方案同步部分已经基本完成，文档已与 Stage-13 的 V3 Admin Vite 模板二次开发方案保持一致；但由于仍存在 `ai_invocations.is_deleted` 这种明确的 Schema 不一致 SQL 示例，本轮结论为“需要继续修改”。

本次仅进行文档复审，未发布新的开发任务，未进入新的阶段。
