# REVIEW-DOC-FIX: 前端模板方案同步文档修复复审报告

## 1. 审查结论

**需要继续修改**

Cursor 已修复上一轮两个主要问题：

1. `docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md` 的 10.3 查询模型调用统计 SQL 已移除 `i.is_deleted = 0`，改为通过 `project_tasks` 和 `projects` 过滤有效任务 / 项目；
2. `docs/project_development_doc.md` 不再是 0 字节空文件，已写明正式项目开发文档位置。

但本轮按用户给出的复审标准继续检查时，发现 2.5 仍未完整列出产品设计参考项目：文档未在 2.5 中明确写入 `One API` 和 `New API`。因此暂不判定通过。

## 2. 上轮问题修复情况

### 2.1 `ai_invocations.is_deleted` 问题

**已修复。**

当前 10.3 SQL 为：

```sql
FROM ai_invocations i
JOIN ai_models m ON i.model_id = m.model_id
JOIN project_tasks t ON i.task_id = t.task_id AND t.is_deleted = 0
JOIN projects p ON t.project_id = p.project_id AND p.is_deleted = 0
GROUP BY m.display_name
```

未再引用不存在的 `i.is_deleted` 字段，符合当前数据库 Schema。

### 2.2 `docs/project_development_doc.md` 空文件问题

**已修复。**

当前文件内容说明其为早期占位文件，并指向正式文档：

```text
docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md
```

不再是 0 字节空文件。

## 3. 仍需修改的问题

### P1. 2.5 产品设计参考项目列表仍不完整

位置：

- `docs/AI项目协作质量审计系统_项目开发文档_整合修订版.md`
- 2.5 借鉴边界与合规说明

当前表述：

```text
本项目在产品设计层面参考 LiteLLM、Dify、Langfuse、Helicone、Open WebUI、LobeChat 等开源项目的功能思想和交互结构；
```

问题：

用户要求 2.5 明确写明产品设计层面参考：

- LiteLLM
- One API
- New API
- Dify
- Langfuse
- Helicone
- Open WebUI
- LobeChat

当前 2.5 缺少 `One API` 和 `New API`。虽然 2.4 中有 One API / New API 的单独介绍，但 2.5 是合规边界总结章节，应显式列出，避免前后不一致。

建议修改为：

```text
本项目在产品设计层面参考 LiteLLM、One API、New API、Dify、Langfuse、Helicone、Open WebUI、LobeChat 等开源项目的功能思想和交互结构；在前端工程实现层面，基于成熟 Vue3 开源后台模板 V3 Admin Vite 进行二次开发。
```

## 4. 其他复查结果

已确认：

1. 2.6 已改为“基于 Vue3 开源后台模板的前端实现方案”；
2. 8.1 已说明前端基于 V3 Admin Vite 二次开发；
3. 8.4 已改为 V3 Admin Vite 裁剪后的目录结构；
4. 9.1 已说明基于 V3 Admin Vite 成熟后台风格进行二次设计；
5. 11.4 已改为引入并裁剪 V3 Admin Vite 模板；
6. 未发现 `/api/auth/register`；
7. 未发现 `rr.status`；
8. 未发现 `code: 200`；
9. 未发现错误的 `task_name / task_type` 请求字段；
10. 未发现与 V3 Admin Vite 二次开发方案冲突的旧表述。

## 5. 是否通过

**暂不通过。**

只剩一个文档表述问题：2.5 需要补齐 `One API` 和 `New API`。修复后可判定文档与 Stage-13 前端方案保持一致。

本次仅进行文档复审，未发布新的开发任务，未进入新的阶段。
