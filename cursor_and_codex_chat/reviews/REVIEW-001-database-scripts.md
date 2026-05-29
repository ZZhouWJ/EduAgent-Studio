# REVIEW-001：Stage-01 数据库脚本审查

## 复审记录

复审时间：2026-05-29

用户已修复 `docs/00` 到 `docs/03` 四个规范文件为空的问题。复查确认：

- `docs/00_AI开发总控规范.md`：281 行
- `docs/01_数据库Schema冻结说明.md`：189 行
- `docs/02_接口契约与页面清单.md`：248 行
- `docs/03_阶段任务卡与验收清单.md`：295 行

因此，上一版审查中的“P1：四个 docs 文件为空”已解决，不再作为阻塞项。

## 审查结论

结论：不通过，需要 Cursor 修复 SQL 后重新提交审查。

是否允许进入 Stage-02：不允许。

原因：`database/` 下 7 个 SQL 文件均存在，整体覆盖了 27 张表、初始化数据、视图、触发器、存储过程和测试查询，但当前脚本按顺序执行仍会在 Stage-01 阶段失败，尚未达到“SQL 文件可按顺序执行；外键无错误；高级特性可运行”的验收标准。

## 已确认通过的部分

1. 7 个 SQL 文件均存在：
   - `database/01_create_database.sql`
   - `database/02_create_tables.sql`
   - `database/03_create_indexes.sql`
   - `database/04_insert_initial_data.sql`
   - `database/05_create_views.sql`
   - `database/06_create_stored_procedures.sql`
   - `database/07_test_queries.sql`
2. `02_create_tables.sql` 中包含 27 个 `CREATE TABLE`，表名覆盖 Schema 清单。
3. 核心业务表普遍包含 `is_deleted`、`deleted_at`、`deleted_by` 以及创建/更新审计字段。
4. `ai_models` 已包含 `input_price`、`output_price`、`price_unit`。
5. `task_outputs` 已包含 `parent_output_id`、`source_type`、`lock_version`、`last_modified_at`、`last_modified_by`、`edit_summary`、`is_final_candidate`。
6. `api_configs` 已包含 `encrypted_api_key`、`key_iv`、`key_tag`、`key_version`、`key_mask`，未保存明文 API Key。
7. 关键状态枚举大体符合冻结设计：`users.status`、`projects.status`、`project_tasks.status`、`task_branches.status`、`review_requests.request_status`、`task_outputs.source_type`、`ai_invocations.status` 均已覆盖。
8. 初始化数据包含角色、权限、管理员、任务类型、问题标签、模型供应商、模型和 API 配置占位数据。
9. 视图、触发器、存储过程、递归查询测试均有设计痕迹，方向符合课程要求。
10. 四份开发规范文档已恢复内容，可以继续作为后续阶段开发约束。

## 阻塞问题

### P0-1：`task_branches` 表重复定义 `created_by` 列，建表必然失败

位置：`database/02_create_tables.sql:345` 和 `database/02_create_tables.sql:351`

问题：同一个 `CREATE TABLE task_branches` 中出现两次 `created_by`。MySQL 会报 `Duplicate column name created_by`，导致后续所有脚本无法继续执行。

修复建议：保留一个 `created_by` 字段即可。建议保留全局审计字段中的 `created_by`，删除前面业务字段重复定义。课程版不建议为此新增字段或更改 Schema。

### P0-2：`task_branches` 在 `task_outputs` 创建前引用 `task_outputs(output_id)`，外键顺序错误

位置：`database/02_create_tables.sql:339-361`

问题：`task_branches.base_output_id` 通过外键引用 `task_outputs.output_id`，但 `task_outputs` 在后面才创建。MySQL 创建外键时要求被引用表已存在，因此 `02_create_tables.sql` 按顺序执行会失败。

修复建议：处理循环依赖。推荐做法：

1. 创建 `task_branches` 时先不声明 `fk_task_branches_base_output`；
2. 创建 `task_outputs` 后，再用 `ALTER TABLE task_branches ADD CONSTRAINT fk_task_branches_base_output ...` 添加该外键；
3. 或者调整设计，避免 `task_branches` 与 `task_outputs` 双向强外键循环。

### P0-3：`03_create_indexes.sql` 与 `02_create_tables.sql` 存在大量重复索引名，顺序执行会失败

位置：`database/03_create_indexes.sql:10-57` 等多处

问题：`02_create_tables.sql` 已经内联创建了大量索引，`03_create_indexes.sql` 再次用相同名称创建。复查脚本检测到 38 个重复索引名，例如：

- `idx_projects_owner`
- `idx_tasks_project_status`
- `idx_review_requests_status`
- `idx_operation_logs_user_time`
- `idx_cost_records_invocation`
- `idx_task_branches_task`

MySQL 会报 `Duplicate key name`。

修复建议：二选一：

1. 保留建表文件中的必要主键、唯一约束和外键辅助索引，把普通二级索引统一移到 `03_create_indexes.sql`；
2. 或保留 `02_create_tables.sql` 中的内联索引，删除 `03_create_indexes.sql` 中重复创建的索引，只留下真正补充索引。

按阶段文件职责，更推荐方案 1：`02_create_tables.sql` 只放表、主键、唯一约束、外键；`03_create_indexes.sql` 放普通查询索引。

### P0-4：`07_test_queries.sql` 中插入 `task_branches` 时重复写入 `created_by` 列

位置：`database/07_test_queries.sql:158`、`database/07_test_queries.sql:214`

问题：测试插入语句列清单为：

```sql
INSERT INTO task_branches (project_id, task_id, branch_name, created_by, status, created_by)
```

即使修复建表重复列，这两条测试 SQL 仍会因重复列名失败。

修复建议：删除重复的第二个 `created_by` 列及对应值，改为：

```sql
INSERT INTO task_branches (project_id, task_id, branch_name, created_by, status)
```

## 需要修复但不单独阻塞 Stage-01 结构完整性的风险

### P1-1：`05_create_views.sql` 使用固定 `DEFINER = root@%`

位置：`database/05_create_views.sql:15`、`70`、`127`、`176`、`216`

问题：课程验收环境不一定允许当前用户创建带 `root@%` DEFINER 的视图。若导入用户不是 root，可能出现权限错误。

修复建议：删除显式 `DEFINER = root@%`，改用普通：

```sql
CREATE VIEW v_xxx AS ...
```

或使用当前执行用户的默认 DEFINER。

### P1-2：`sp_complete_review` 的参数使用 `ENUM(...)`，可移植性和可执行性风险较高

位置：`database/06_create_stored_procedures.sql:454`

问题：存储过程参数 `p_review_status ENUM(approved,rejected,revision_required)` 对 MySQL 版本/模式兼容性不如 `VARCHAR` 稳定，也不利于未来适配 SQL Server。

修复建议：改为 `VARCHAR(30)`，在过程内部用 `IF p_review_status NOT IN (...)` 做显式校验。

## 非阻塞建议

1. `ai_invocations`、`cost_records`、`operation_logs`、`login_logs` 当前没有外键约束。作为审计表可以接受，但建议在文档中说明这是为了避免审计数据被业务删除影响。
2. 初始化数据没有插入 `prompt_templates` 和 `prompt_versions`。这不阻塞 Stage-01，但 Stage-06 或 Stage-07 前需要补充，否则生成流程缺少可直接选择的提示词版本。
3. `07_test_queries.sql` 会插入大量测试数据，建议后续增加“清理测试数据”小节，方便重复执行。
4. `01_create_database.sql` 包含 `DROP DATABASE IF EXISTS`，适合重建测试库，但正式交付说明中应提醒该脚本会清空已有数据库。

## 对照审查清单

| 检查项 | 结论 |
|---|---|
| 7 个 SQL 文件是否存在 | 通过 |
| 27 张表是否完整 | 通过 |
| 主键、外键、唯一约束、非空约束是否合理 | 需要修改，存在建表顺序外键问题 |
| 核心业务表是否有软删除字段 | 通过 |
| `ai_models` 计费字段 | 通过 |
| `task_outputs` 版本/乐观锁字段 | 通过 |
| `api_configs` 加密字段 | 通过 |
| ENUM 状态值是否一致 | 基本通过 |
| 初始化数据是否完整 | 基本通过，建议补充提示词模板 |
| 视图、触发器、存储过程是否满足课程要求 | 有覆盖，但需修复可执行性风险 |
| `07_test_queries.sql` 是否能验证关键功能 | 有覆盖，但当前存在重复列错误，不能完整执行 |
| 是否可以进入 Stage-02 | 不可以 |

## Cursor 修复要求

请 Cursor 只修改 Stage-01 允许范围：`database/*.sql`。禁止修改 `backend/` 和 `frontend/`。

修复后请重新提交 Stage-01，并至少说明：

1. 7 个 SQL 文件按顺序执行是否成功；
2. 27 张表是否成功创建；
3. 索引是否无重复；
4. 视图是否创建成功；
5. 触发器是否创建成功；
6. 存储过程是否创建成功；
7. `07_test_queries.sql` 是否可完整执行或哪些测试需要手动执行。
