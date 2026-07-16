-- Replace untouched project-output placeholders with task-specific deliverables.
USE `ai_collab_audit_system`;

CREATE TEMPORARY TABLE `seed_project_output_contents` (
    `task_title` VARCHAR(200) PRIMARY KEY,
    `content` LONGTEXT NOT NULL
);

INSERT INTO `seed_project_output_contents` (`task_title`, `content`) VALUES
('事务隔离级别图解讲义', '# 事务隔离级别图解讲义

## 学习目标
理解脏读、不可重复读和幻读的产生条件，并能根据一致性要求与并发代价选择隔离级别。

## 并发现象
| 现象 | 过程 | 风险 |
| --- | --- | --- |
| 脏读 | T1 修改后未提交，T2 已读到该值，随后 T1 回滚 | T2 基于不存在的数据继续计算 |
| 不可重复读 | T1 两次读取同一行，期间 T2 提交了更新 | 同一事务内行值不一致 |
| 幻读 | T1 两次执行同一范围查询，期间 T2 插入或删除匹配行 | 结果集行数发生变化 |

## 隔离级别
- **读未提交**：允许读取未提交数据，并发高但一致性风险最大。
- **读已提交**：每条语句读取已提交快照，可避免脏读。
- **可重复读**：事务内保持一致快照；具体幻读行为取决于数据库实现与锁策略。
- **串行化**：效果接近事务顺序执行，一致性最强，但等待与死锁概率上升。

## 判断方法
先标出每个事务的读写对象和提交点，再判断后一次读取是否必须看到前一次相同的版本。不要仅凭隔离级别名称推断，应结合数据库实现、查询范围和锁信息验证。

## 自检
库存扣减、余额查询和月度报表分别需要什么隔离保证？请说明允许出现的偏差、锁等待上限和失败重试策略。'),
('多表连接练习题集', '# 多表连接练习题集

## 数据模型
使用学生 student、课程 course、教师 teacher、选课 enrollment、成绩 score 五张表。先画出主外键关系，再完成查询。

## 基础题（1-6）
1. 查询每名学生及其已选课程名称。
2. 查询每门课程及授课教师姓名。
3. 列出选修数据库课程的学生学号与姓名。
4. 查询每名学生的课程数，未选课学生也要显示为 0。
5. 查询没有任何学生选修的课程。
6. 查询同时选修数据库和 Python 的学生。

## 进阶题（7-14）
7. 统计每门课程的平均分、最高分与最低分。
8. 查询平均分高于全校平均分的学生。
9. 查询每门课程成绩排名前三的学生，正确处理并列。
10. 找出选课人数高于本院课程平均选课人数的课程。
11. 查询至少教授两门课程的教师及课程数。
12. 查询选修了某教师全部课程的学生。
13. 找出只选修一门课程且成绩及格的学生。
14. 查询每个院系平均分最高的课程。

## 综合题（15-20）
15. 生成学生成绩单，包含课程、学分、成绩和加权平均分。
16. 查询连续两个学期成绩提升的学生。
17. 识别同一时间段存在课程冲突的选课记录。
18. 查询先修课未通过却选修后续课程的学生。
19. 使用窗口函数统计课程成绩分位数，并解释与子查询方案的差异。
20. 为第 7、9、12 题分析执行计划并提出索引方案。

## 提交与评分
每题提交 SQL、结果行数和边界说明。正确性占 60%，空值与重复行处理占 20%，可读性占 10%，执行计划与索引依据占 10%。'),
('银行转账并发案例', '# 银行转账并发案例

## 场景
账户 A 向账户 B 转账 500 元，同时账户 A 可能收到另一笔扣款。系统必须保证余额不为负、借贷两端金额守恒、重复请求不会重复入账。

## 初始数据
account(id, balance, version) 保存余额，transfer(id, request_no, from_id, to_id, amount, status) 保存转账流水，其中 request_no 唯一。

## 并发风险
1. 两个事务先后读取相同余额并分别扣减，造成丢失更新。
2. 借方已扣款但贷方写入失败，造成金额不守恒。
3. 客户端超时重试，造成同一请求重复转账。
4. 两笔反向转账以不同顺序锁定账户，造成死锁。

## 实现任务
- 在一个数据库事务内创建流水、锁定账户、校验余额、更新双方余额并提交。
- 始终按账户 ID 升序加锁，降低死锁概率。
- 以唯一请求号实现幂等；重复请求返回原流水结果。
- 对死锁与锁等待超时采用有上限的退避重试，并记录审计事件。

## 验证
并发执行 100 组转账，校验总余额不变、无负余额、请求号唯一、失败事务不产生单边记账。报告隔离级别、SQL、锁顺序、重试次数和最终校验结果。'),
('Flask 路由与蓝图', '# Flask 路由与蓝图

## 学习目标
掌握 URL 规则、HTTP 方法、请求参数与响应状态码，并使用蓝图拆分可独立维护的业务模块。

## 路由契约
路由函数负责把 HTTP 请求转换为业务调用，再把结果转换为响应。参数校验失败返回 400，未认证返回 401，无权限返回 403，资源不存在返回 404；不要把所有异常都返回 200。

```python
students = Blueprint("students", __name__, url_prefix="/api/students")

@students.get("/<int:student_id>")
def get_student(student_id: int):
    student = student_service.get(student_id)
    if student is None:
        return {"message": "student not found"}, 404
    return student.to_dict(), 200
```

## 蓝图组织
- routes.py：声明路径、方法、输入与响应。
- service.py：实现业务规则，不依赖 Flask 全局请求对象。
- repository.py：封装持久化操作。
- errors.py：统一业务异常到 HTTP 响应的映射。

在应用工厂中注册蓝图，测试环境可注入独立配置与存储。跨域、鉴权、日志与追踪应通过扩展或中间件统一处理。

## 练习
实现学生列表和详情接口，支持分页与姓名筛选；分别测试成功、参数非法、资源不存在和仓储异常，确认状态码与错误结构一致。'),
('Python 函数练习', '# Python 函数练习

## 要求
每题写出函数签名、类型标注、边界约定和至少两个测试用例。除题目明确允许外，不修改传入对象。

1. clamp(value, lower, upper)：将数值限制在闭区间内，并校验上下界。
2. deduplicate(items)：保持原顺序去重，支持不可哈希元素时给出明确策略。
3. group_by(items, key)：按回调结果分组，返回字典。
4. moving_average(values, window)：计算滑动平均，处理窗口大于序列长度的情况。
5. retry(operation, attempts, retry_on)：对指定异常执行有限重试。
6. parse_score(text)：解析成绩字符串，拒绝空值、非数字和区间外数值。
7. compose(*functions)：从右到左组合单参数函数。
8. summarize(records, field)：统计指定字段的数量、均值、最小值和最大值。
9. memoize(function)：实现保留函数元信息的简单缓存装饰器，并说明参数限制。
10. batch(items, size)：将可迭代对象按固定大小分批，最后一批允许不足。

## 评分标准
正确性 50%，边界与异常 20%，类型和可读性 15%，测试覆盖 15%。测试至少包含正常输入、空输入和一个非法输入。'),
('数据看板实战案例', '# 数据看板实战案例

## 业务目标
为课程负责人构建学习数据看板，回答活跃学生数量、任务完成趋势、知识点薄弱分布和高风险学生变化四个问题。

## 数据与指标
- 学生活跃：按自然日去重的有效学习事件用户数。
- 任务完成率：截止时间内完成任务数除以到期任务数。
- 知识点掌握：最近有效测评按时间衰减后的加权结果。
- 风险学生：连续 7 天无学习、逾期任务不少于 2 个或掌握度显著下降。

## 实现任务
1. 使用 Flask 蓝图实现 /api/dashboard/summary 与 /api/dashboard/trends。
2. 在服务层定义统计口径、时间范围和权限范围，禁止学生读取全班数据。
3. 对高频聚合增加合适索引与短时缓存，并提供缓存失效策略。
4. 前端实现指标概览、趋势图、薄弱知识点排序和风险学生表格。
5. 为无数据、部分数据失败、超时和窄屏场景提供明确状态。

## 验收标准
接口口径可追溯，测试数据下计算结果准确；教师只能访问本人课程；图表有标题、单位和可读的键盘替代信息；首屏接口在目标数据量下 P95 小于 800ms。'),
('Scrum 角色与流程总结', '# Scrum 角色与流程总结

## 三类责任
- **Product Owner**：最大化产品价值，管理并排序 Product Backlog，确保目标和条目清晰。
- **Scrum Master**：帮助团队理解并实践 Scrum，移除组织障碍，促进持续改进。
- **Developers**：共同制定 Sprint Backlog、保证交付质量，并对可用增量负责。

## 核心流程
1. Product Backlog 持续梳理，条目围绕产品目标排序。
2. Sprint Planning 明确 Sprint Goal，选择条目并制定实现计划。
3. Daily Scrum 检查实现 Sprint Goal 的进展并调整当天计划。
4. Sprint Review 与利益相关者检查增量并调整后续方向。
5. Sprint Retrospective 改进人员、协作、流程和工具。

## 三个工件及承诺
Product Backlog 对应 Product Goal，Sprint Backlog 对应 Sprint Goal，Increment 对应 Definition of Done。只有满足完成定义的工作才能计入增量。

## 常见误区
Daily Scrum 不是向管理者汇报；Scrum Master 不是任务分配者；Sprint Review 不是单纯演示会；未完成条目不能通过降低质量标准“转为完成”。团队应以透明、检查和适应形成可持续反馈闭环。'),
('团队迭代 1 评审', '# 团队迭代 1 评审报告

## 评审范围
本次评审覆盖预约查询、预约创建、冲突检测与取消流程，以及对应需求、接口文档、自动化测试和部署说明。

## 结论
核心主流程可运行，但当前版本暂不满足发布条件。冲突检测在并发请求下缺少数据库唯一约束，取消操作未记录操作者与原因，接口错误结构也不一致。

## 发现
| 级别 | 问题 | 验收证据 |
| --- | --- | --- |
| 阻断 | 并发创建可能产生重叠预约 | 增加约束或事务锁，并通过并发测试 |
| 高 | 取消记录缺少审计字段 | 审计日志包含用户、时间、原因和原状态 |
| 中 | 400 与 404 响应结构不统一 | 契约测试覆盖全部公开接口 |
| 中 | 部署文档未说明回滚 | 提供版本回退和数据库兼容步骤 |

## 后续行动
负责人在下一次提交前修复阻断与高等级问题，补充并发、权限和回滚测试。修复后由评审人复核证据；中等级问题进入下一 Sprint，但必须明确负责人和截止时间。

## 通过条件
阻断和高等级问题归零，核心端到端测试通过，部署与回滚演练完成，遗留风险得到 Product Owner 明确认可。');

UPDATE `task_outputs` o
JOIN `project_tasks` pt ON pt.`task_id` = o.`task_id`
JOIN `seed_project_output_contents` seed ON seed.`task_title` = pt.`title`
SET o.`content` = seed.`content`
WHERE o.`is_deleted` = 0
  AND o.`content` LIKE '%AI 生成内容%';

UPDATE `ai_invocations` i
JOIN `project_tasks` pt ON pt.`task_id` = i.`task_id`
JOIN `seed_project_output_contents` seed ON seed.`task_title` = pt.`title`
SET i.`output_text` = seed.`content`
WHERE i.`is_deleted` = 0
  AND i.`output_text` LIKE '%演示内容%';

DROP TEMPORARY TABLE `seed_project_output_contents`;
