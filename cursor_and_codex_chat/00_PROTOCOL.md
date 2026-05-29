# Cursor 与 Codex 协作协议

## 1. 角色分工

### Codex
Codex 是项目总览者、代码审查者、任务发布者。

Codex 负责：
1. 阅读 docs/ 下的开发规范；
2. 阅读当前代码和 Git diff；
3. 发布阶段任务；
4. 审查 Cursor 的代码修改；
5. 判断是否通过验收；
6. 写出下一步任务；
7. 维护 PROJECT_STATUS.md 和 TASK_BOARD.md。

Codex 原则上不直接实现业务代码，除非用户明确要求。

### Cursor
Cursor 是代码实现者。

Cursor 负责：
1. 领取 Codex 发布的任务；
2. 按任务卡修改代码；
3. 运行测试；
4. 写交接报告；
5. 根据 Codex 审查意见修复问题。

Cursor 不得自行跳阶段，不得自行修改技术栈，不得自行更改 Schema。

---

## 2. 协作流程

1. Codex 在 tasks/todo/ 创建任务文件；
2. Cursor 读取任务文件；
3. Cursor 将任务状态改为 doing；
4. Cursor 修改代码；
5. Cursor 运行测试；
6. Cursor 在 handoff/ 写完成报告；
7. Codex 审查代码和报告；
8. Codex 在 reviews/ 写审查结果；
9. 如果不通过，Cursor 根据 reviews/ 修改；
10. 如果通过，Codex 将任务移动到 tasks/done/，并发布下一任务。

---

## 3. 文件夹说明

- tasks/todo：待领取任务
- tasks/doing：正在执行任务
- tasks/blocked：阻塞任务
- tasks/done：已完成任务
- reviews：Codex 审查意见
- handoff：Cursor 交接报告
- decisions：重要架构决策记录
- logs：协作日志
- prompts：给 Codex 和 Cursor 的固定提示词
- archive：历史归档

---

## 4. 任务文件命名规则

任务文件统一命名：

TASK-编号-简短说明.md

例如：

TASK-002-backend-base.md
TASK-003-auth-user-permission.md

---

## 5. 审查文件命名规则

审查文件统一命名：

REVIEW-编号-任务说明.md

例如：

REVIEW-002-backend-base.md

---

## 6. 严禁事项

1. 不得跳过 Codex 审查直接进入下一阶段；
2. 不得让 Cursor 自行决定阶段目标；
3. 不得让 Codex 直接大规模改代码；
4. 不得把任务描述写成"把整个项目做完"；
5. 不得修改 docs/01_数据库Schema冻结说明.md，除非用户确认；
6. 不得绕过参数化 SQL；
7. 不得删除软删除、审计日志、乐观锁、安全字段。
