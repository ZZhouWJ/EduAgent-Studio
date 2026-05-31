# TASK-011：统计看板与课程展示数据模块

## 任务状态

已完成。

## 一、任务目标

完成统计看板与课程展示数据模块，为首页、项目详情、模型调用、成本、审核质量、成员贡献和最近操作动态提供后端统计接口。

本阶段只允许实现后端统计查询接口，不实现前端页面，不修改数据库结构。

## 二、允许实现范围

1. 首页统计概览接口；
2. 项目统计接口；
3. 模型调用统计接口；
4. 成本统计接口；
5. 审核质量统计接口；
6. 成员贡献统计接口；
7. 最近操作动态接口；
8. 统计相关 SQL 查询和视图调用。

## 三、建议接口

以 `docs/02_接口契约与页面清单.md` 为准。如文档未细化，可按以下接口实现：

1. `GET /api/statistics/dashboard`
2. `GET /api/statistics/projects`
3. `GET /api/statistics/models`
4. `GET /api/statistics/costs`
5. `GET /api/statistics/reviews`
6. `GET /api/statistics/members`
7. `GET /api/statistics/recent-activities`

接口命名如需与契约文档保持一致，以契约文档优先。

## 四、允许修改文件

- `backend/app/routers/statistics.py`
- `backend/app/services/statistics_service.py`
- `backend/app/repositories/statistics_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-011-statistics-dashboard.md`

## 五、禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 六、禁止实现

1. 前端页面；
2. 数据库结构修改。

## 七、验收重点

### 1. 权限控制

- admin 可以查看全局统计；
- 普通项目成员只能查看自己参与项目相关统计；
- 非项目成员不能查看无关项目统计；
- 模型、成本、审核、贡献统计不得泄露其他项目数据；
- 权限判断应基于已有用户角色和项目成员关系。

### 2. 首页统计概览

应返回课程展示常用概览数据，例如：

- 项目数量；
- 任务数量；
- 输出版本数量；
- 待审核数量；
- 已采用成果数量；
- 模型调用次数；
- 成本总额；
- 最近操作摘要。

具体字段可按现有数据结构合理组织，但必须使用统一返回格式。

### 3. 项目统计

- 可统计项目任务数量、输出数量、审核状态分布、成果数量；
- 可优先调用已有视图，如 `v_project_task_statistics`；
- 查询默认过滤业务表 `is_deleted = 0`；
- 支持按 `project_id` 查询；
- 普通用户只能看自己参与项目。

### 4. 模型调用统计

- 统计调用次数、成功/失败数量、token 数、平均耗时；
- 可按项目、任务、模型、时间范围过滤；
- 不返回完整 input_text / output_text；
- 不返回 API Key、加密字段或密钥字段；
- 可优先调用已有视图，如 `v_model_invocation_statistics`。

### 5. 成本统计

- 基于 `cost_records`；
- 统计 total_tokens、input_cost、output_cost、total_cost；
- 可按项目、任务、模型、用户、时间范围过滤；
- 成本查询不得越权。

### 6. 审核质量统计

- 基于 `review_requests`、`output_reviews`、`issue_tags`、`output_issue_relations`；
- 可统计审核结论分布、平均评分、问题标签分布；
- 查询默认过滤软删除记录；
- 不泄露其他项目审核数据。

### 7. 成员贡献统计

- 基于 `project_members`、`project_tasks`、`task_outputs`、`operation_logs`、`ai_invocations` 等；
- 可统计成员任务数、输出数、审核数、采用成果数、模型调用数；
- 普通成员只能查看本项目内贡献统计。

### 8. 最近操作动态

- 基于 `operation_logs`；
- admin 可查看全局；
- 项目成员只能查看自己参与项目动态；
- 返回操作类型、对象、操作者、时间等必要信息；
- 不返回敏感字段或原始异常堆栈。

### 9. 数据库访问

- SQL 集中在 `statistics_repo.py`；
- 全部使用参数化 SQL；
- 不使用 ORM；
- 不拼接用户输入；
- 查询默认过滤 `is_deleted = 0`；
- 统计接口以只读查询为主，不写业务表；
- 如调用视图，需保证视图字段与 `database/05_create_views.sql` 一致。

### 10. 统一返回和错误处理

- 成功响应使用统一格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 权限不足、资源不存在、参数错误使用统一错误格式；
- 不向前端暴露原始异常堆栈。

## 八、完成后 handoff 要求

Cursor 完成后必须创建：

`cursor_and_codex_chat/handoff/HANDOFF-011-statistics-dashboard.md`

handoff 至少说明：

1. 实现接口清单；
2. 修改文件清单；
3. 权限规则；
4. 每类统计的数据来源；
5. 是否调用数据库视图；
6. 是否未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
7. Python 语法检查结果；
8. 当前环境限制。

