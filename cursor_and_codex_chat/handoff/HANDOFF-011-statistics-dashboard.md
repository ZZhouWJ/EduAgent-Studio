# HANDOFF-011：Stage-11 统计看板与课程展示数据模块

## 任务状态

**完成** — Stage-11 统计看板后端接口已实现。

---

## 一、本次修改文件

| 文件 | 操作 | 说明 |
| --- | --- | --- |
| `backend/app/repositories/statistics_repo.py` | 新建 | 7 个统计接口的所有 SQL |
| `backend/app/services/statistics_service.py` | 新建 | 权限校验 + 业务逻辑 |
| `backend/app/routers/statistics.py` | 新建 | 7 个 API 路由 |
| `backend/app/main.py` | 修改 | 注册 `statistics.router` |
| `cursor_and_codex_chat/handoff/HANDOFF-011-statistics-dashboard.md` | 新建 | 本交接报告 |

**说明**：未修改 `database/*`、`frontend/*`、`docs/*`。

---

## 二、实现内容

### Repository 层（`statistics_repo.py`）

| 函数 | 说明 | 数据来源 |
|---|---|---|
| `get_overview_stats` | 首页统计概览（10 项指标）| projects, project_tasks, review_requests, ai_invocations, adopted_outputs, cost_records |
| `list_project_stats` | 项目统计列表 | v_project_task_statistics 视图 |
| `get_project_stats_by_id` | 单项目详细统计 | v_project_task_statistics 视图 |
| `get_model_call_stats` | 模型调用统计 | ai_invocations + v_model_invocation_statistics 视图 |
| `get_cost_stats` | 成本统计（总体 + 按模型/项目/用户）| cost_records |
| `get_review_stats` | 审核质量统计 | review_requests, output_reviews, issue_tags, output_issue_relations |
| `get_member_contribution_stats` | 成员贡献统计 | project_members + 关联子查询 |
| `get_recent_activities` | 最近操作动态 | operation_logs |
| `check_user_can_access_project` | 项目访问权限判断 | project_members |
| `_build_project_filter` | 项目过滤条件构建器 | project_members（用于非 admin）|

### Service 层（`statistics_service.py`）

| 函数 | 说明 |
|---|---|
| `get_overview` | 首页概览（权限 + 调用 repo）|
| `list_project_stats` | 项目统计列表（权限 + 调用 repo）|
| `get_model_call_stats` | 模型调用统计（日期校验 + 权限 + 调用 repo）|
| `get_cost_stats` | 成本统计（日期校验 + 权限 + 调用 repo）|
| `get_review_stats` | 审核质量统计（权限 + 调用 repo）|
| `get_member_contribution_stats` | 成员贡献统计（权限 + 调用 repo）|
| `get_recent_activities` | 最近操作动态（limit 校验 + 权限 + 调用 repo）|
| `_validate_date` | 日期格式 YYYY-MM-DD 校验 |

### Router 层（`statistics.py`）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/statistics/overview` | 首页统计概览 |
| GET | `/api/statistics/projects` | 项目统计 |
| GET | `/api/statistics/model-calls` | 模型调用统计 |
| GET | `/api/statistics/costs` | 成本统计 |
| GET | `/api/statistics/reviews` | 审核质量统计 |
| GET | `/api/statistics/member-contributions` | 成员贡献统计 |
| GET | `/api/statistics/recent-activities` | 最近操作动态 |

---

## 三、数据库是否变化

**否**。未修改 `database/*`，未修改表结构。

---

## 四、新增接口列表

```
GET /api/statistics/overview
GET /api/statistics/projects
GET /api/statistics/model-calls
GET /api/statistics/costs
GET /api/statistics/reviews
GET /api/statistics/member-contributions
GET /api/statistics/recent-activities
```

---

## 五、统计指标说明

### 5.1 首页概览（overview）

| 字段 | 说明 |
|---|---|
| project_count | 项目总数 |
| active_project_count | 进行中项目数 |
| task_count | 任务总数 |
| pending_review_count | 待审核数量（review_requests.request_status = 'pending'）|
| invocation_count | 模型调用总数 |
| success_invocation_count | 成功调用数 |
| failed_invocation_count | 失败调用数 |
| artifact_count | 成果数量 |
| total_tokens | 总 token 数（input + output）|
| total_cost | 总成本 |

### 5.2 模型调用统计

| 字段 | 说明 |
|---|---|
| model_id | 模型 ID |
| model_name | 模型名称 |
| display_name | 显示名称 |
| provider_name | 提供商名称 |
| total_invocations | 调用总次数 |
| success_count | 成功次数 |
| failed_count | 失败次数 |
| timeout_count | 超时次数 |
| blocked_count | 阻塞次数 |
| total_input_tokens | 输入 token 总数 |
| total_output_tokens | 输出 token 总数 |
| total_tokens | token 总数 |
| avg_latency_ms | 平均延迟（毫秒）|
| success_rate | 成功率（百分比）|

### 5.3 成本统计

| 字段 | 说明 |
|---|---|
| total_cost | 总成本 |
| input_cost | 输入成本 |
| output_cost | 输出成本 |
| total_tokens | 总 token 数 |
| currency | 货币，固定为 CNY |
| cost_by_model | 按模型分成本列表 |
| cost_by_project | 按项目分成本列表 |
| cost_by_user | 按用户分成本列表 |

### 5.4 审核质量统计

| 字段 | 说明 |
|---|---|
| review_count | 审核总数 |
| approved_count | 通过数 |
| rejected_count | 拒绝数 |
| revision_required_count | 需修改数 |
| avg_accuracy_score | 平均准确性评分 |
| avg_completeness_score | 平均完整性评分 |
| avg_logic_score | 平均逻辑性评分 |
| avg_format_score | 平均格式评分 |
| avg_usability_score | 平均可用性评分 |
| avg_risk_score | 平均风险评分 |
| top_issue_tags | Top 10 问题标签（tag_name, tag_code, severity, tag_count）|

### 5.5 成员贡献统计

| 字段 | 说明 |
|---|---|
| user_id | 用户 ID |
| real_name | 用户姓名 |
| project_count | 参与项目数 |
| task_created_count | 创建任务数 |
| task_assigned_count | 被分配任务数 |
| output_created_count | 创建输出数 |
| review_count | 审核数 |
| artifact_adopted_count | 采用成果数 |
| invocation_count | 模型调用数 |

### 5.6 最近操作动态

| 字段 | 说明 |
|---|---|
| log_id | 日志 ID |
| user_id | 用户 ID |
| real_name | 用户姓名 |
| action_type | 操作类型 |
| target_type | 目标类型 |
| target_id | 目标 ID |
| action_desc | 操作描述 |
| created_at | 操作时间 |

---

## 六、权限规则说明

| 角色 | overview | projects | model-calls | costs | reviews | member-contributions | recent-activities |
|---|---|---|---|---|---|---|---|
| admin | 全局 | 全局 | 全局 | 全局 | 全局 | 全局 | 全局 |
| 项目成员 | 本项目 | 本项目 | 本项目 | 本项目 | 本项目 | 本项目 | 本项目 |
| 非成员 | 无权 | 无权 | 无权 | 无权 | 无权 | 无权 | 无权 |

**核心原则**：所有接口传入 `project_id` 时，后端 service 层通过 `check_user_can_access_project` 校验权限，不依赖前端传参。

---

## 七、是否使用数据库视图

**是**。使用了以下视图：

| 视图 | 用途 |
|---|---|
| `v_project_task_statistics` | 项目统计列表和单项目详情 |
| `v_model_invocation_statistics` | 模型调用统计（模型维度聚合）|

注意：`v_model_invocation_statistics` 是全局视图，project_id 和日期过滤通过 JOIN `ai_invocations` 附加条件实现。

---

## 八、是否使用 GROUP BY / 聚合 SQL

**是**。所有统计接口均使用 COUNT、SUM、AVG、COALESCE、CASE WHEN、GROUP BY 等聚合函数。

---

## 九、敏感字段过滤说明

| 字段类型 | 处理方式 |
|---|---|
| password_hash | 不查询 |
| api_key / encrypted_api_key | 不查询 |
| key_iv / key_tag | 不查询 |
| input_text / output_text | 不在列表接口返回 |
| email / phone | 只在成本按用户统计中返回 real_name，不返回 email/phone |

---

## 十、overview 测试方法

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<USER>","password":"<PWD>"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

curl "http://127.0.0.1:8000/api/statistics/overview" \
  -H "Authorization: Bearer $TOKEN"
```

期望：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "project_count": 2,
    "active_project_count": 2,
    "task_count": 5,
    "pending_review_count": 1,
    "invocation_count": 20,
    "success_invocation_count": 18,
    "failed_invocation_count": 2,
    "artifact_count": 3,
    "total_tokens": 125000,
    "total_cost": 12.50
  }
}
```

---

## 十一、model-calls 测试方法

```bash
# 全部
curl "http://127.0.0.1:8000/api/statistics/model-calls" \
  -H "Authorization: Bearer $TOKEN"

# 按项目过滤
curl "http://127.0.0.1:8000/api/statistics/model-calls?project_id=1" \
  -H "Authorization: Bearer $TOKEN"

# 按日期范围
curl "http://127.0.0.1:8000/api/statistics/model-calls?date_from=2025-01-01&date_to=2025-12-31" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十二、costs 测试方法

```bash
curl "http://127.0.0.1:8000/api/statistics/costs" \
  -H "Authorization: Bearer $TOKEN"

curl "http://127.0.0.1:8000/api/statistics/costs?project_id=1&date_from=2025-01-01&date_to=2025-12-31" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十三、reviews 测试方法

```bash
curl "http://127.0.0.1:8000/api/statistics/reviews" \
  -H "Authorization: Bearer $TOKEN"

curl "http://127.0.0.1:8000/api/statistics/reviews?project_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十四、member-contributions 测试方法

```bash
# 全部成员贡献（admin）
curl "http://127.0.0.1:8000/api/statistics/member-contributions" \
  -H "Authorization: Bearer $TOKEN"

# 按项目过滤
curl "http://127.0.0.1:8000/api/statistics/member-contributions?project_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十五、recent-activities 测试方法

```bash
curl "http://127.0.0.1:8000/api/statistics/recent-activities" \
  -H "Authorization: Bearer $TOKEN"

curl "http://127.0.0.1:8000/api/statistics/recent-activities?project_id=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 十六、已知问题

1. **当前环境无 MySQL**：无法真实执行 SQL 验证，所有验证基于静态代码审查
2. **聚合查询性能**：成员贡献统计使用子查询，高并发大表场景可能需要索引优化，但不影响正确性

---

## 十七、是否实现前端页面

**否**。

---

## 十八、是否修改 database

**否**。

---

## 十九、Python 语法检查命令

```bash
cd backend
python -m py_compile app/repositories/statistics_repo.py app/services/statistics_service.py app/routers/statistics.py app/main.py
```

结果：`EXIT:0`（通过）。

---

## 二十、当前环境限制

- 当前环境无 MySQL，无法真实执行 SQL 验证
- 本次基于静态代码审查，不因无法连接 MySQL 阻塞
- 未修改 `database/` 目录，未修改表结构

---

## 二十一、需要 Codex 审查的重点

1. **权限规则**：admin / 非 admin 项目成员的数据范围是否正确隔离；`project_id` 参数是否在后端被强制校验
2. **视图使用**：`v_project_task_statistics` 和 `v_model_invocation_statistics` 字段是否与 Schema 一致
3. **参数化 SQL**：所有 SQL 是否使用 `%s` 参数绑定，无字符串拼接
4. **敏感字段**：是否确认不返回 `password_hash`、`api_key`、`encrypted_api_key`、`key_iv`、`key_tag`
5. **NULL 处理**：`COALESCE` 和 `_normalize_row` 是否正确处理聚合结果中的 NULL
6. **AVG 空结果**：审核评分 AVG 查询中，当无评分记录时是否返回 0 而非报错
7. **limit 限制**：`recent_activities` 的 limit 是否在 router 层限制最大 100
8. **日期校验**：`date_from` / `date_to` 是否正确校验 YYYY-MM-DD 格式
9. **无越界**：确认未实现前端页面、未修改 `database/*`
10. **repo 纯度**：`statistics_repo.py` 是否包含所有 SQL，service 层无内联 SQL

---

## 二十二、验收清单

- [x] `GET /api/statistics/overview` 实现（10 项指标）
- [x] `GET /api/statistics/projects` 实现（使用视图）
- [x] `GET /api/statistics/model-calls` 实现（支持过滤）
- [x] `GET /api/statistics/costs` 实现（按模型/项目/用户分组）
- [x] `GET /api/statistics/reviews` 实现（评分 + 问题标签）
- [x] `GET /api/statistics/member-contributions` 实现（7 项贡献指标）
- [x] `GET /api/statistics/recent-activities` 实现（limit <= 100）
- [x] admin 可查看全局统计
- [x] 非 admin 只查看参与项目范围统计
- [x] project_id 参数后端权限校验
- [x] 使用 `v_project_task_statistics` 视图
- [x] 使用 `v_model_invocation_statistics` 视图
- [x] 参数化 SQL，无字符串拼接
- [x] 不返回敏感字段
- [x] COALESCE 处理聚合 NULL
- [x] limit 最大 100 限制
- [x] 日期格式 YYYY-MM-DD 校验
- [x] SQL 集中于 statistics_repo.py
- [x] service 层无内联 SQL
- [x] 未修改 `database/*`、`frontend/*`、`docs/*`
- [x] Python 语法检查通过

---

**本阶段完成后停止，等待 Codex 审查。**
