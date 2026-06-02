# 任务看板

## 当前总览

项目已完成 Stage-01 到 Stage-17 的分阶段开发、审查、修复复审与最终收尾文档复审，当前进入最终验收准备。

> 注意：远程 Ubuntu / WSL 环境无法直接完成 Windows MySQL 与 Node 前端构建联调；仍需在本地 Windows MySQL + Node 环境补做实际运行截图和联调验证。

| 编号 | 阶段 | 任务 | 状态 | 负责人 | 审查人 |
|---|---|---|---|---|---|
| TASK-001 | Stage-01 | 数据库脚本 | 已通过 R3 静态审查 | Cursor | Codex |
| TASK-002 | Stage-02 | FastAPI 后端基础框架 | 已通过 | Cursor | Codex |
| TASK-003 | Stage-03 | 用户登录与权限基础模块 | 已通过 Fix R2 复审 | Cursor | Codex |
| TASK-004 | Stage-04 | 项目空间管理模块 | 已通过 Fix R2 复审 | Cursor | Codex |
| TASK-005 | Stage-05 | 任务与版本管理模块 | 已通过 Fix 复审 | Cursor | Codex |
| TASK-006 | Stage-06 | 提示词模板管理模块 | 已通过 | Cursor | Codex |
| TASK-007 | Stage-07 | 模型管理、Mock 调用、日志和成本记录 | 已通过 Fix R2 复审 | Cursor | Codex |
| TASK-008 | Stage-08 | 人工编辑、批注与乐观锁模块 | 已通过 Fix 复审 | Cursor | Codex |
| TASK-009 | Stage-09 | 审核中心模块 | 已通过 Fix R3 复审 | Cursor | Codex |
| TASK-010 | Stage-10 | 成果库与分支合并模块 | 已通过 Fix R2 复审 | Cursor | Codex |
| TASK-011 | Stage-11 | 统计看板与课程展示数据模块 | 已通过 Fix R3 复审 | Cursor | Codex |
| TASK-012 | Stage-12 | 后端整体联调、运行验证与课程报告素材整理 | 已通过 Fix R2 复审 | Cursor | Codex |
| TASK-013 | Stage-13 | Vue3 前端基础框架、登录页和整体布局 | 已通过 Fix R2 复审 | Cursor | Codex |
| TASK-014 | Stage-14 | 前端项目空间、任务与版本基础页面 | 已通过 Fix 复审 | Cursor | Codex |
| TASK-015 | Stage-15 | 前端 AI 生成、输出编辑与批注交互页面 | 已通过 Fix 复审 | Cursor | Codex |
| TASK-016 | Stage-16 | 前端审核中心、成果库与统计看板页面 | 已通过 Fix 复审 | Cursor | Codex |
| TASK-017 | Stage-17 | 最终润色、运行说明、截图清单与课程报告素材 | 已通过 Fix R2 复审，已移入 done | Cursor | Codex |

## 当前待办

- 本地 Windows MySQL 环境执行 `database/01` 到 `database/07` SQL 导入与验证；
- 本地 Node 环境执行前端依赖安装与构建验证；
- 启动后端、前端并补做关键接口联调截图；
- 按 `docs/截图清单.md`、`docs/系统测试与结果分析素材.md`、`docs/最终检查清单.md` 完成课程验收材料截图。
