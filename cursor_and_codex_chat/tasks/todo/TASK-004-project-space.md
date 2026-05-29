# TASK-004：Stage-04 项目空间管理模块

## 任务状态

已完成。

## 任务背景

Stage-03 用户登录与权限基础模块已通过 Codex 复审。现在进入 Stage-04：项目空间管理模块。

本阶段只允许实现项目空间与项目成员管理，不得进入任务管理、AI 调用、提示词模板、审核中心、成果库或前端页面。

## 任务目标

完成项目空间管理模块，包括：

1. 项目列表接口；
2. 项目创建接口；
3. 项目详情接口；
4. 项目更新接口；
5. 项目软删除接口；
6. 项目成员列表接口；
7. 添加项目成员接口；
8. 修改项目成员角色接口；
9. 移除项目成员接口；
10. 项目一键归档接口；
11. 项目相关操作日志写入。

## 允许修改文件

只允许修改或创建以下文件：

- `backend/app/routers/projects.py`
- `backend/app/services/project_service.py`
- `backend/app/repositories/project_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-004-project-space.md`

如确实需要复用当前用户权限工具，可少量修改：

- `backend/app/services/auth_service.py`
- `backend/app/repositories/user_repo.py`
- `backend/app/utils/token.py`

但必须在 `HANDOFF-004-project-space.md` 中说明理由、修改范围和对 Stage-03 的影响。

## 禁止修改文件

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 禁止实现内容

Stage-04 禁止实现：

1. 任务管理；
2. AI 调用；
3. 提示词模板；
4. 审核中心；
5. 成果库；
6. 前端页面。

## 接口范围

必须遵守 `docs/02_接口契约与页面清单.md` 中的项目与成员接口，不得自行发明接口路径。

建议实现：

- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}`
- `PUT /api/projects/{project_id}`
- `DELETE /api/projects/{project_id}`
- `POST /api/projects/{project_id}/archive`
- `GET /api/projects/{project_id}/members`
- `POST /api/projects/{project_id}/members`
- `PUT /api/projects/{project_id}/members/{member_id}`
- `DELETE /api/projects/{project_id}/members/{member_id}`

如发现接口契约不足，必须先在 handoff 中提出接口变更申请，不得直接新增未约定接口。

## 数据表范围

本阶段只允许围绕以下表进行查询或写入：

- `projects`
- `project_members`
- `users`
- `operation_logs`

不得修改数据库结构，不得新增表、字段、状态值或枚举值。

## 权限要求

1. 管理员可以查看和管理所有项目；
2. 项目负责人可以查看和管理自己负责的项目；
3. 普通成员只能查看自己参与的项目；
4. 添加、移除成员和修改成员角色应限制为管理员或项目负责人；
5. 项目归档应限制为管理员或项目负责人；
6. 所有鉴权失败必须使用统一错误响应。

## 数据库与事务要求

1. 使用 Repository 层封装 SQL；
2. SQL 必须使用参数化查询；
3. 不得使用 ORM 替代核心 SQL；
4. 普通查询必须默认过滤 `is_deleted = 0`；
5. 删除项目必须软删除，设置 `is_deleted`、`deleted_at`、`deleted_by`；
6. 移除项目成员必须软删除项目成员记录；
7. 创建项目后必须自动将创建人写入 `project_members`；
8. 创建项目、软删除项目、添加成员、移除成员、修改成员角色、项目归档必须写入 `operation_logs`；
9. 创建项目、软删除项目、成员变更、项目归档属于关键操作，必须使用事务保证一致性。

## 统一返回格式

所有接口必须使用 Stage-02 已建立的统一返回格式。

成功响应：

```json
{"code": 0, "message": "success", "data": {}}
```

错误响应：

```json
{"code": 4001, "message": "权限不足", "data": null}
```

分页响应：

```json
{"code": 0, "message": "success", "data": {"items": [], "total": 0, "page": 1, "page_size": 10}}
```

## 验收清单

Cursor 完成后请确认：

1. 项目列表支持分页和权限过滤；
2. 项目创建成功后自动写入项目负责人到 `project_members`；
3. 项目详情只允许有权限的用户查看；
4. 项目更新只允许管理员或项目负责人操作；
5. 项目删除为软删除，不得物理删除；
6. 项目成员列表可查询；
7. 添加项目成员可用，且不能重复添加未删除成员；
8. 修改项目成员角色可用，枚举值必须使用 `member / leader / reviewer / teacher`；
9. 移除成员为软删除；
10. 项目归档将项目状态设为 `archived`；
11. 项目相关关键操作写入 `operation_logs`；
12. 所有 SQL 使用参数化查询；
13. 未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
14. 未实现任务管理、AI 调用、提示词模板、审核中心、成果库或前端页面。

## 交付要求

完成后请创建：

`cursor_and_codex_chat/handoff/HANDOFF-004-project-space.md`

handoff 必须说明：

1. 修改了哪些文件；
2. 实现了哪些接口；
3. 权限规则如何实现；
4. 哪些操作使用了事务；
5. 哪些操作写入了 `operation_logs`；
6. 安装依赖命令，如无新增依赖请明确说明；
7. 启动命令；
8. 接口测试方法；
9. 是否需要数据库初始化数据支持；
10. 已知限制或待 Codex 审查事项。
