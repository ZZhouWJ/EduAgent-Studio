"""
课程文档加载器。

预置「数据库系统原理与 Web 项目实践」课程的核心知识点文档片段。
这些片段作为轻量 RAG 知识库，无需外部 embedding API 即可检索。

文档格式：dict { chunk_id, title, content, kp_name, source }
"""

import re
from typing import List, Dict, Any


# ============================================================
# 课程核心知识库 — 数据库系统原理与 Web 项目实践
# 课程 ID: 1
# ============================================================

COURSE_MATERIALS: List[Dict[str, Any]] = [
    # ---------- 关系模型基础 ----------
    {
        "chunk_id": "db001-1",
        "title": "关系模型基础 — 核心概念",
        "kp_name": "关系模型基础",
        "kp_code": "DB001",
        "course_id": 1,
        "content": """## 关系模型基础

### 基本概念
关系（Relation）：一个关系就是一张二维表，每一行称为一个元组（Tuple），每一列称为一个属性（Attribute）。

### 关键术语
- **主键（Primary Key）**：唯一标识元组的属性或属性组，不能为空且不能重复
- **外键（Foreign Key）**：引用另一个表主键的字段，用于建立表之间的关联
- **候选键（Candidate Key）**：能唯一标识元组的最小属性集
- **超键（Super Key）**：包含候选键的属性集

### 关系完整性约束
1. **实体完整性**：主键属性不能为空
2. **参照完整性**：外键要么为空，要么必须参照另一个表的主键
3. **用户定义完整性**：应用系统自定义的约束条件

### 关系代数运算
- **选择（σ）**：按条件筛选行
- **投影（π）**：按列筛选
- **连接（⋈）**：将两个表按条件拼接

来源：数据库系统原理（第3版），高等教育出版社，第3章""",
        "source": "教材第3章 关系模型基础",
    },
    {
        "chunk_id": "db001-2",
        "title": "关系模型基础 — ER 图设计",
        "kp_name": "关系模型基础",
        "kp_code": "DB001",
        "course_id": 1,
        "content": """## ER 图与关系模型转换

### ER 图基本元素
- **实体集**：用矩形表示，对应数据库中的一张表
- **属性**：用椭圆表示，对应表中的列
- **联系集**：用菱形表示，表示实体之间的关系

### ER 图到关系模型的转换规则
1. 实体集 → 表：实体集的所有属性构成表的结构
2. 一对一联系：可将联系属性合并到任意一端实体对应的表中
3. 一对多联系：在多端实体对应的表中添加一端实体的主键作为外键
4. 多对多联系：必须创建一张新的关系表，包含两个实体集的主键作为联合主键

### 示例
学生（学号，姓名，专业）与课程（课程号，课程名，学分）之间是多对多关系，
需要创建选课表（学号，课程号，成绩）来表达。

来源：数据库系统原理（第3版），高等教育出版社，第4章""",
        "source": "教材第4章 ER模型",
    },

    # ---------- SQL 基本查询 ----------
    {
        "chunk_id": "db002-1",
        "title": "SQL 基本查询 — SELECT/FROM/WHERE",
        "kp_name": "SQL基本查询",
        "kp_code": "DB002",
        "course_id": 1,
        "content": """## SQL 基本查询

### 最基础的 SELECT 语句
```sql
SELECT 列名1, 列名2
FROM 表名
WHERE 条件
ORDER BY 列名 ASC|DESC;
```

### WHERE 子句常用条件
- **比较运算符**：=、<>、<、>、<=、>=
- **逻辑运算符**：AND、OR、NOT
- **范围判断**：BETWEEN ... AND ...
- **集合判断**：IN、NOT IN
- **模糊匹配**：LIKE（% 任意字符，_ 单个字符）
- **空值判断**：IS NULL、IS NOT NULL

### 常用聚合函数
- COUNT()：统计数量
- SUM()：求和
- AVG()：求平均值
- MAX()：最大值
- MIN()：最小值

### GROUP BY 与 HAVING
```sql
SELECT 专业, COUNT(*) AS 人数
FROM 学生表
GROUP BY 专业
HAVING COUNT(*) > 10;
```
HAVING 用于对分组后的结果进行筛选（WHERE 用于分组前）。

来源：数据库系统原理（第3版），高等教育出版社，第5章 SQL基础""",
        "source": "教材第5章 SQL查询基础",
    },
    {
        "chunk_id": "db002-2",
        "title": "SQL 高级查询 — 子查询与集合运算",
        "kp_name": "SQL基本查询",
        "kp_code": "DB002",
        "course_id": 1,
        "content": """## SQL 子查询与集合运算

### 子查询（Subquery）
子查询是嵌套在另一个查询中的 SELECT 语句。

**标量子查询**：返回单一值，用于比较条件
```sql
SELECT * FROM 学生表
WHERE 年龄 > (SELECT AVG(年龄) FROM 学生表);
```

**列子查询**：返回一列值，用于 IN/NOT IN
```sql
SELECT * FROM 课程表
WHERE 课程号 IN (SELECT 课程号 FROM 选课表 WHERE 成绩 > 90);
```

**表子查询**：返回一张表，用于 FROM 子句
```sql
SELECT * FROM (SELECT * FROM 学生表 WHERE 专业='CS') AS T;
```

### EXISTS 与 NOT EXISTS
```sql
-- 选了课的学生
SELECT * FROM 学生表 S
WHERE EXISTS (
    SELECT 1 FROM 选课表 C WHERE C.学号 = S.学号
);
```

### 集合运算
- **UNION**：合并（自动去重）
- **UNION ALL**：合并（不去重，效率更高）
- **INTERSECT**：交集
- **EXCEPT**：差集

来源：数据库系统原理（第3版），高等教育出版社，第6章 SQL高级查询""",
        "source": "教材第6章 子查询与集合运算",
    },

    # ---------- DDL ----------
    {
        "chunk_id": "db003-1",
        "title": "数据定义 DDL — 表结构管理",
        "kp_name": "数据定义DDL",
        "kp_code": "DB003",
        "course_id": 1,
        "content": """## DDL 数据定义语言

### CREATE TABLE 创建表
```sql
CREATE TABLE 学生表 (
    学号 VARCHAR(20) PRIMARY KEY,
    姓名 VARCHAR(50) NOT NULL,
    年龄 INT CHECK (年龄 BETWEEN 16 AND 60),
    专业 VARCHAR(100),
    入学日期 DATE DEFAULT '2026-09-01',
    UNIQUE(姓名, 专业)
);
```

### 常用约束
- **NOT NULL**：非空约束
- **UNIQUE**：唯一约束
- **PRIMARY KEY**：主键（自动 NOT NULL + UNIQUE）
- **FOREIGN KEY ... REFERENCES**：外键约束
- **CHECK**：检查约束
- **DEFAULT**：默认值
- **AUTO_INCREMENT**：自增字段（MySQL 语法）

### ALTER TABLE 修改表结构
```sql
-- 添加列
ALTER TABLE 学生表 ADD COLUMN 邮箱 VARCHAR(100);
-- 删除列
ALTER TABLE 学生表 DROP COLUMN 邮箱;
-- 修改列类型
ALTER TABLE 学生表 MODIFY COLUMN 年龄 INT;
-- 添加外键
ALTER TABLE 选课表 ADD FOREIGN KEY (学号) REFERENCES 学生表(学号);
```

来源：数据库系统原理（第3版），高等教育出版社，第5章 DDL语句""",
        "source": "教材第5章 数据定义",
    },

    # ---------- 多表连接 ----------
    {
        "chunk_id": "db005-1",
        "title": "SQL 多表连接 — JOIN 类型详解",
        "kp_name": "SQL多表连接",
        "kp_code": "DB005",
        "course_id": 1,
        "content": """## SQL 多表连接

### 内连接（INNER JOIN）
只返回两个表中满足连接条件的元组。
```sql
SELECT S.姓名, C.课程名, G.成绩
FROM 学生表 S
INNER JOIN 选课表 G ON S.学号 = G.学号
INNER JOIN 课程表 C ON G.课程号 = C.课程号;
```

### 外连接
**左外连接（LEFT JOIN）**：返回左表所有记录，右表无匹配时用 NULL 填充。
```sql
-- 所有学生的选课情况，没选课的也显示
SELECT S.学号, S.姓名, G.成绩
FROM 学生表 S
LEFT JOIN 选课表 G ON S.学号 = G.学号;
```

**右外连接（RIGHT JOIN）**：返回右表所有记录，左表无匹配时用 NULL 填充。
```sql
SELECT S.学号, S.姓名, G.成绩
FROM 学生表 S
RIGHT JOIN 选课表 G ON S.学号 = G.学号;
```

**全外连接（FULL OUTER JOIN）**：返回两表所有记录，无匹配处用 NULL 填充。
```sql
SELECT S.学号, S.姓名, G.成绩
FROM 学生表 S
FULL OUTER JOIN 选课表 G ON S.学号 = G.学号;
```

### 自然连接（NATURAL JOIN）
自动按同名列进行等值连接，慎用！
```sql
SELECT * FROM 学生表 NATURAL JOIN 选课表;
```

### 自连接
同一张表与自身连接，常用于层级数据（如员工与上司）。
```sql
SELECT E.员工姓名 AS 员工, M.员工姓名 AS 上司
FROM 员工表 E
LEFT JOIN 员工表 M ON E.上司编号 = M.员工编号;
```

来源：数据库系统原理（第3版），高等教育出版社，第6章 多表连接""",
        "source": "教材第6章 多表连接",
    },
    {
        "chunk_id": "db005-2",
        "title": "多表连接 — 常见错误与优化",
        "kp_name": "SQL多表连接",
        "kp_code": "DB005",
        "course_id": 1,
        "content": """## 多表连接常见错误与优化建议

### 常见错误
1. **笛卡尔积**：忘记写连接条件会产生笛卡尔积（行数相乘），查询极慢
2. **歧义列名**：多表有同名列时必须加表别名限定
3. **外键缺失**：连接条件与外键不一致
4. **NULL 值**：使用 = 比较 NULL 永远返回 UNKNOWN，需用 IS NULL

### 优化建议
1. **小表驱动大表**：LEFT JOIN 时将小表放左边，INNER JOIN 时让有索引的表作为驱动表
2. **减少 SELECT ***：只查需要的列，减少网络传输和内存占用
3. **分步查询**：复杂多表连接可拆成多个简单查询，先看中间结果
4. **避免嵌套子查询**：用连接（JOIN）替代相关子查询

### 正确示例（3表连接）
```sql
-- 查询选了「数据库系统」且成绩 >= 85 的学生姓名和成绩
SELECT DISTINCT S.姓名, G.成绩
FROM 学生表 S
JOIN 选课表 G ON S.学号 = G.学号
JOIN 课程表 C ON G.课程号 = C.课程号
WHERE C.课程名 = '数据库系统' AND G.成绩 >= 85;
```

来源：数据库系统原理（第3版）实践指导，第4章""",
        "source": "教材实践指导第4章",
    },

    # ---------- 事务隔离级别 ----------
    {
        "chunk_id": "db008-1",
        "title": "事务与并发控制 — ACID 特性",
        "kp_name": "事务隔离级别",
        "kp_code": "DB008",
        "course_id": 1,
        "content": """## 事务与 ACID 特性

### 什么是事务
事务（Transaction）是数据库中一组不可分割的逻辑工作单元，要么全部执行，要么全部不执行。

### ACID 四大特性
1. **Atomicity（原子性）**：事务是最小执行单位，不可再分。提交成功则全部生效，回滚则全部撤销。
2. **Consistency（一致性）**：事务执行前后，数据库从一个一致状态变到另一个一致状态。
3. **Isolation（隔离性）**：并发执行的事务互不干扰，各自独立。
4. **Durability（持久性）**：事务提交后，对数据库的修改是永久性的。

### SQL 中的事务控制
```sql
START TRANSACTION;  -- 或 BEGIN
-- 一系列 SQL 操作
COMMIT;             -- 提交
-- 或
ROLLBACK;           -- 回滚
```

### 事务边界与自动提交
- MySQL 默认 autocommit=1，每条 SQL 自动构成一个事务
- InnoDB 引擎支持事务，MyISAM 不支持
- 生产环境中，重要操作前应显式 START TRANSACTION

来源：数据库系统原理（第3版），高等教育出版社，第8章 事务管理""",
        "source": "教材第8章 事务管理",
    },
    {
        "chunk_id": "db008-2",
        "title": "事务隔离级别 — 四种级别详解",
        "kp_name": "事务隔离级别",
        "kp_code": "DB008",
        "course_id": 1,
        "content": """## 四种事务隔离级别

### 并发问题
| 问题 | 说明 |
|------|------|
| 脏读（Dirty Read） | 读取到其他事务未提交的数据 |
| 不可重复读（Non-repeatable Read）| 同一事务中两次读取同一行，结果不同（因其他事务更新并提交）|
| 幻读（Phantom Read）| 同一事务中两次查询，结果集行数不同（因其他事务插入/删除）|

### 四种隔离级别
| 级别 | 脏读 | 不可重复读 | 幻读 | 说明 |
|------|------|-----------|------|------|
| READ UNCOMMITTED | 可能 | 可能 | 可能 | 最低隔离，最低保护 |
| READ COMMITTED | 不可能 | 可能 | 可能 | 大多数数据库默认（Oracle）|
| REPEATABLE READ | 不可能 | 不可能 | 可能 | MySQL 默认 |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 | 最高隔离，性能最差 |

### SQL 设置隔离级别
```sql
-- 会话级别（当前连接）
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- 全局级别
SET GLOBAL transaction_isolation = 'REPEATABLE-READ';
```

### MySQL InnoDB 的 REPEATABLE READ
InnoDB 在 REPEATABLE READ 级别下通过 MVCC（多版本并发控制）解决了幻读问题，
使用 Next-Key Lock 锁定索引范围，而非锁整个表。

来源：数据库系统原理（第3版），高等教育出版社，第8章隔离级别""",
        "source": "教材第8章 隔离级别",
    },
    {
        "chunk_id": "db008-3",
        "title": "并发控制 — 锁机制",
        "kp_name": "事务隔离级别",
        "kp_code": "DB008",
        "course_id": 1,
        "content": """## 并发控制 — 锁机制

### 锁的类型
1. **共享锁（S 锁）**：读锁，多个事务可同时持有，不互斥
   ```sql
   SELECT * FROM 表 WHERE ... LOCK IN SHARE MODE;
   ```

2. **排他锁（X 锁）**：写锁，一旦某事务持有，其他事务不能同时持有
   ```sql
   SELECT * FROM 表 WHERE ... FOR UPDATE;
   ```

### 锁粒度
- **行级锁**：锁一行，粒度最细，并发最高，MySQL InnoDB
- **表级锁**：锁整张表，粒度最粗，并发最低，MyISAM
- **页级锁**：锁一页，介于行级和表级之间

### 死锁
两个或多个事务互相持有对方需要的锁，形成循环等待。
MySQL InnoDB 的死锁处理：检测到死锁后回滚持有最少行级锁的事务。

### 乐观锁 vs 悲观锁
- **悲观锁**：假设并发冲突高，先加锁再操作（SELECT ... FOR UPDATE）
- **乐观锁**：假设并发冲突低，不加锁，通过版本号比较解决冲突
  ```sql
  UPDATE 账户表 SET 余额 = 余额 - 100, 版本号 = 版本号 + 1
  WHERE 账户号 = 1 AND 版本号 = 5;
  ```

来源：数据库系统原理（第3版），高等教育出版社，第9章 并发控制""",
        "source": "教材第9章 并发控制",
    },

    # ---------- 数据库范式 ----------
    {
        "chunk_id": "db012-1",
        "title": "数据库范式 — 1NF/2NF/3NF/BCNF",
        "kp_name": "数据库范式",
        "kp_code": "DB012",
        "course_id": 1,
        "content": """## 数据库规范化理论

### 函数依赖
设 X、Y 是关系 R 的属性集，若 X 的值能唯一确定 Y 的值，则称 **X → Y**（X 函数决定 Y）。
- **完全函数依赖**：X 的任何真子集都不能决定 Y
- **部分函数依赖**：X 的某个真子集能决定 Y
- **传递函数依赖**：X → Y，Y ↛ X，Y → Z，则 X → Z（传递）

### 范式等级
**1NF（第一范式）**：属性不可再分（原子性）
❌ 错误：`地址 = "北京市海淀区"`（可再分为省、市、区）

**2NF（第二范式）**：满足 1NF，且非主属性完全函数依赖于主键
❌ 错误：学生成绩表（学号, 课程号, 学生姓名, 成绩）—— 学生姓名部分函数依赖于学号

**3NF（第三范式）**：满足 2NF，且非主属性不传递依赖于主键
❌ 错误：学生表（学号, 姓名, 专业, 学院）—— 学号→专业，专业→学院，存在传递依赖

**BCNF（BC范式）**：满足 3NF，且主属性对主键完全函数依赖
- 任何时候一个表中只有一个候选键

### 范式化与反范式化
- 范式化：减少数据冗余，保证数据一致性（3NF 足够）
- 反范式化：为提升查询性能，故意引入数据冗余

来源：数据库系统原理（第3版），高等教育出版社，第7章 规范化理论""",
        "source": "教材第7章 规范化理论",
    },

    # ---------- 索引与优化 ----------
    {
        "chunk_id": "db015-1",
        "title": "索引与查询优化 — B+Tree 索引原理",
        "kp_name": "索引与优化",
        "kp_code": "DB015",
        "course_id": 1,
        "content": """## 索引与查询优化

### MySQL InnoDB 索引原理
InnoDB 使用 **B+Tree** 作为索引结构（所有索引都是 B+Tree）。

**B+Tree 特性**：
- 所有数据都存储在叶子节点
- 叶子节点之间用双向链表连接（范围查询快）
- 非叶子节点只存储索引列的值和指针
- 树高通常 2-4 层，能覆盖千万级数据

### 索引类型
1. **主键索引（PRIMARY KEY）**：自动创建，唯一且非空
2. **唯一索引（UNIQUE）**：值唯一，可为空
3. **普通索引（INDEX）**：无限制
4. **全文索引（FULLTEXT）**：用于文本内容搜索
5. **复合索引**：多列组合（最左前缀原则）

### 最左前缀原则
```sql
-- 创建复合索引
CREATE INDEX idx_name ON 学生表(专业, 年龄, 姓名);
-- 以下查询能使用索引：
-- (专业)、(专业, 年龄)、(专业, 年龄, 姓名)
-- 以下查询无法使用索引：
-- (年龄)、(姓名)
```

### SQL 性能优化建议
1. **避免 SELECT ***：只查需要的列
2. **避免 LIKE '%xxx'**：前缀通配符无法使用索引
3. **OR 改 UNION**：OR 条件可能导致索引失效，改 UNION ALL 效率更高
4. **JOIN 优化**：小表驱动大表，关联列有索引
5. **EXPLAIN 分析**：`EXPLAIN SELECT ...` 查看执行计划

来源：数据库系统原理（第3版），高等教育出版社，第10章 查询优化""",
        "source": "教材第10章 查询优化",
    },
]


def get_all_chunks() -> List[Dict[str, Any]]:
    """返回所有课程文档片段。"""
    return COURSE_MATERIALS


def get_chunks_by_kp(kp_name: str) -> List[Dict[str, Any]]:
    """根据知识点名称筛选文档片段。"""
    return [c for c in COURSE_MATERIALS if c["kp_name"] == kp_name]


def get_chunks_by_ids(chunk_ids: List[str]) -> List[Dict[str, Any]]:
    """根据 chunk_id 列表获取文档片段。"""
    id_set = set(chunk_ids)
    return [c for c in COURSE_MATERIALS if c["chunk_id"] in id_set]
