# TASK-010：成果库与分支合并模块

## 一、任务目标

完成成果库与分支合并模块，实现审核通过输出的成果采用、成果查询、分支冲突处理与合并记录写入。

本阶段只允许实现后端成果库与分支合并相关接口，不实现统计看板和前端页面。

## 二、允许实现范围

1. 采用成果接口；
2. 项目成果列表接口；
3. 成果详情接口；
4. 分支冲突处理接口；
5. 分支合并记录 `merge_records` 写入；
6. `adopted_outputs` 写入；
7. `task_outputs` 状态更新；
8. `task_branches` 状态更新；
9. 采用与合并相关 `operation_logs` 写入。

## 三、建议接口

以 `docs/02_接口契约与页面清单.md` 为准。如文档未细化，可按以下最小接口实现：

1. `POST /api/outputs/{output_id}/adopt`
2. `GET /api/projects/{project_id}/artifacts`
3. `GET /api/artifacts/{artifact_id}`
4. `POST /api/tasks/{task_id}/branches/merge`

接口命名如需与既有契约保持一致，以契约文档优先。

## 四、允许修改文件

- `backend/app/routers/artifacts.py`
- `backend/app/services/artifact_service.py`
- `backend/app/repositories/artifact_repo.py`
- `backend/app/main.py`
- `cursor_and_codex_chat/handoff/HANDOFF-010-artifact-library.md`

如确实需要复用任务、输出或审核权限判断，可少量修改：

- `backend/app/services/task_service.py`
- `backend/app/repositories/task_repo.py`
- `backend/app/services/review_service.py`
- `backend/app/repositories/review_repo.py`

但必须在 handoff 中说明修改原因、修改范围和未越界承诺。

## 五、禁止修改

- `database/*`
- `frontend/*`
- `docs/01_数据库Schema冻结说明.md`

## 六、禁止实现

1. 统计看板；
2. 前端页面。

## 七、验收重点

### 1. 采用成果

- 只允许有项目权限的用户操作；
- 非项目成员不能采用成果；
- output 必须存在且未删除；
- output 状态应为 `approved` 或符合契约要求的可采用状态；
- 写入 `adopted_outputs`；
- 更新 `task_outputs.status = adopted`；
- 写入 `operation_logs`；
- 采用成果相关写操作必须在同一事务中；
- 不得物理删除任何记录。

### 2. 项目成果列表和详情

- 项目成果列表只返回当前用户有权限访问的项目成果；
- admin 可查看全部项目成果；
- 项目成员只能查看本项目成果；
- 默认过滤 `is_deleted = 0`；
- 列表接口不返回不必要的大字段；
- 详情接口可返回成果内容和来源输出信息；
- 不返回 `password_hash`、API Key、加密密钥字段等敏感信息。

### 3. 分支冲突处理和合并

- 分支、任务、项目上下文必须校验一致；
- 只能处理当前用户有权限访问的任务分支；
- `merge_strategy` 必须使用 Schema 冻结文档允许值：
  - `adopt_source`
  - `adopt_target`
  - `manual_merge`
  - `adopt_separately`
- 写入 `merge_records`；
- 根据策略合理更新 `task_outputs.status` 和 `task_branches.status`；
- 写入 `operation_logs`；
- 合并相关写操作必须在同一事务中；
- 不得越权合并其他项目分支。

### 4. 数据库访问

- SQL 集中在 `artifact_repo.py`；
- 全部使用参数化 SQL；
- 不使用 ORM；
- 不拼接用户输入；
- 多表写入使用事务；
- repository 方法不随意 `commit`；
- service 层统一 `commit / rollback`；
- 关键 `UPDATE` 必须检查 `affected_rows`；
- 连接必须正确关闭。

### 5. 统一返回和错误处理

- 成功响应使用统一格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 权限不足、资源不存在、参数错误、状态不允许等情况使用统一错误格式；
- 不向前端暴露原始异常堆栈。

## 八、完成后 handoff 要求

Cursor 完成后必须创建：

`cursor_and_codex_chat/handoff/HANDOFF-010-artifact-library.md`

handoff 至少说明：

1. 实现的接口清单；
2. 修改文件清单；
3. 权限规则；
4. 采用成果、成果查询、分支合并的事务设计；
5. `adopted_outputs`、`merge_records`、`task_outputs`、`task_branches`、`operation_logs` 写入说明；
6. 是否修改了可选复用文件及理由；
7. 是否未修改 `database/*`、`frontend/*`、`docs/01_数据库Schema冻结说明.md`；
8. Python 语法检查结果；
9. 当前环境限制。

