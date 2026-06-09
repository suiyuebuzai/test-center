# test-center 数据词典

日期：2026-06-05

> 覆盖全部 17 张表，每张表包含：字段说明、数据类型、约束、枚举值。
> 阅读建议：先看 `defects`（核心实体），再看 `applications` → `versions` → `test_cases` 的主干链路。

---

## 目录

| # | 表名 | 模块 | 说明 |
|---|------|------|------|
| 1 | [users](#1-users) | 用户权限 | 系统用户 |
| 2 | [roles](#2-roles) | 用户权限 | 角色定义 |
| 3 | [user_roles](#3-user_roles) | 用户权限 | 用户-角色关联（多对多） |
| 4 | [applications](#4-applications) | 应用管理 | 被测应用 |
| 5 | [versions](#5-versions) | 应用管理 | 应用版本 |
| 6 | [test_cases](#6-test_cases) | 用例管理 | 测试用例库 |
| 7 | [test_tasks](#7-test_tasks) | 测试执行 | 测试任务 |
| 8 | [task_executions](#8-task_executions) | 测试执行 | 用例执行记录 |
| 9 | [defects](#9-defects) | 缺陷管理 | 缺陷（核心实体） |
| 10 | [defect_comments](#10-defect_comments) | 缺陷管理 | 缺陷评论 |
| 11 | [defect_status_history](#11-defect_status_history) | 缺陷管理 | 状态变更历史 |
| 12 | [test_case_defects](#12-test_case_defects) | 缺陷管理 | 用例-缺陷关联（多对多） |
| 13 | [automation_scripts](#13-automation_scripts) | 自动化 | 自动化脚本注册 |
| 14 | [automation_runs](#14-automation_runs) | 自动化 | 自动化执行记录 |
| 15 | [automation_run_details](#15-automation_run_details) | 自动化 | 单用例执行结果 |
| 16 | [perf_scripts](#16-perf_scripts) | 性能测试 | 性能脚本配置 |
| 17 | [perf_runs](#17-perf_runs) | 性能测试 | 性能执行记录 |

---

## 通用约定

| 约定 | 说明 |
|------|------|
| 主键类型 | `UUID`，应用层生成（Python `uuid4()`）|
| 时间类型 | `TIMESTAMP WITH TIME ZONE`，统一存 UTC |
| 软删除 | 核心数据表加 `is_deleted + deleted_at`，不物理删除 |
| 审计字段 | 所有表加 `created_at`；可变表加 `updated_at`；关键表加 `created_by` |
| 字符串枚举 | 用 `VARCHAR` 存枚举值（不用数据库 ENUM 类型），方便迁移和扩展 |
| 外键命名 | `{关联表单数名}_id`，如 `app_id`、`defect_id` |

---

## 1. users

**说明：** 系统用户表，存储登录账号信息。密码不可逆加密存储（bcrypt）。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 用户唯一标识 |
| username | VARCHAR(50) | UNIQUE NOT NULL | 登录用户名，字母数字下划线 |
| email | VARCHAR(255) | UNIQUE NOT NULL | 邮箱，用于通知 |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt 哈希密码，不存明文 |
| is_active | BOOLEAN | NOT NULL DEFAULT true | 是否启用，false=禁用登录 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 注册时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

---

## 2. roles

**说明：** 角色字典表，预置 4 个角色，一般不增减。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | SMALLINT | PK | 角色 ID |
| name | VARCHAR(20) | UNIQUE NOT NULL | 角色标识符，见枚举值 |
| description | VARCHAR(100) | | 角色描述 |

**枚举值（name）：**

| 值 | 说明 | 关键权限 |
|----|------|---------|
| `admin` | 管理员 | 所有操作，包括用户管理、删除数据 |
| `tester` | 测试人员 | 创建/执行用例，创建/验证缺陷 |
| `developer` | 开发人员 | 查看用例，修复缺陷（标 Fixed），不能关闭 |
| `readonly` | 只读用户 | 仅查看，不能创建/修改/删除任何内容 |

---

## 3. user_roles

**说明：** 用户-角色多对多关联表。支持全局角色（app_id=NULL）和应用级角色。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | UUID | PK, FK → users.id | 用户 |
| role_id | SMALLINT | PK, FK → roles.id | 角色 |
| app_id | UUID | PK, FK → applications.id, NULLABLE | NULL=全局，有值=应用级角色 |
| granted_at | TIMESTAMP | NOT NULL DEFAULT now() | 授权时间 |
| granted_by | UUID | FK → users.id | 授权人 |

> **设计说明：** 联合主键 `(user_id, role_id, app_id)`，NULL 参与联合主键时需注意 PostgreSQL 的 NULL 唯一性行为，可用 `COALESCE(app_id, '00000000-...')` 处理或改用唯一索引。

---

## 4. applications

**说明：** 被测应用（项目），是整个系统的顶级组织单元，所有数据都归属于某个应用。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 应用唯一标识 |
| name | VARCHAR(100) | UNIQUE NOT NULL | 应用名称，如"电商平台" |
| code | VARCHAR(20) | UNIQUE NOT NULL | 应用短码，大写字母，如 `MALL`，用于缺陷编号前缀 `MALL-001` |
| description | TEXT | | 应用描述 |
| is_active | BOOLEAN | NOT NULL DEFAULT true | 是否有效，false=归档 |
| is_deleted | BOOLEAN | NOT NULL DEFAULT false | 软删除标志 |
| deleted_at | TIMESTAMP | NULLABLE | 软删除时间 |
| created_by | UUID | FK → users.id | 创建人 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

---

## 5. versions

**说明：** 应用版本，用于追踪"在哪个版本发现 Bug，在哪个版本修复"。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 版本唯一标识 |
| app_id | UUID | NOT NULL, FK → applications.id | 所属应用 |
| name | VARCHAR(50) | NOT NULL | 版本号，如 `v1.2.0`、`Sprint-23` |
| description | TEXT | | 版本说明，包含主要功能点 |
| status | VARCHAR(20) | NOT NULL DEFAULT 'planning' | 版本状态，见枚举值 |
| release_date | DATE | NULLABLE | 计划/实际发布日期 |
| created_by | UUID | FK → users.id | 创建人 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

**唯一约束：** `(app_id, name)`，同一应用下版本名不重复。

**枚举值（status）：**

| 值 | 说明 |
|----|------|
| `planning` | 规划中，未开始测试 |
| `testing` | 测试中 |
| `released` | 已发布 |
| `archived` | 已归档 |

---

## 6. test_cases

**说明：** 测试用例库，属于应用维度，不绑定具体版本（用例是可复用的）。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 用例唯一标识 |
| app_id | UUID | NOT NULL, FK → applications.id | 所属应用 |
| title | VARCHAR(255) | NOT NULL | 用例标题，如"登录-正确账号密码-成功登录" |
| description | TEXT | | 用例描述，背景说明 |
| preconditions | TEXT | | 前置条件，如"用户已注册" |
| steps | JSONB | | 测试步骤，结构化数组，见示例 |
| expected_result | TEXT | | 预期结果 |
| category | VARCHAR(100) | | 功能模块分类，如"登录模块"、"订单流程" |
| priority | VARCHAR(5) | NOT NULL DEFAULT 'P2' | 优先级，见枚举值 |
| case_type | VARCHAR(20) | NOT NULL DEFAULT 'functional' | 用例类型，见枚举值 |
| is_automated | BOOLEAN | NOT NULL DEFAULT false | 是否有自动化脚本覆盖 |
| is_deleted | BOOLEAN | NOT NULL DEFAULT false | 软删除 |
| deleted_at | TIMESTAMP | NULLABLE | 软删除时间 |
| created_by | UUID | FK → users.id | 创建人 |
| updated_by | UUID | FK → users.id | 最后修改人 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

**枚举值（priority）：**

| 值 | 说明 |
|----|------|
| `P0` | 核心功能，必须通过，阻塞发版 |
| `P1` | 重要功能，强烈建议通过 |
| `P2` | 普通功能，正常测试 |
| `P3` | 边缘 Case，时间允许再测 |

**枚举值（case_type）：**

| 值 | 说明 |
|----|------|
| `functional` | 功能测试 |
| `performance` | 性能测试 |
| `security` | 安全测试 |
| `regression` | 回归测试 |
| `smoke` | 冒烟测试 |

**steps 字段示例（JSONB）：**
```json
[
  { "step": 1, "action": "打开登录页面", "expected": "显示登录表单" },
  { "step": 2, "action": "输入正确的用户名和密码", "expected": "输入无报错" },
  { "step": 3, "action": "点击登录按钮", "expected": "跳转到首页，显示用户名" }
]
```

---

## 7. test_tasks

**说明：** 测试任务，关联版本，用于安排一轮测试工作。一个版本可以有多轮测试任务（如"第一轮全量测试"、"回归测试"）。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 任务唯一标识 |
| app_id | UUID | NOT NULL, FK → applications.id | 所属应用 |
| version_id | UUID | NOT NULL, FK → versions.id | 所属版本 |
| name | VARCHAR(255) | NOT NULL | 任务名称，如"v1.2.0 第一轮全量测试" |
| description | TEXT | | 任务说明 |
| status | VARCHAR(20) | NOT NULL DEFAULT 'pending' | 任务状态，见枚举值 |
| assignee_id | UUID | FK → users.id, NULLABLE | 任务负责人 |
| start_date | DATE | NULLABLE | 计划开始日期 |
| due_date | DATE | NULLABLE | 计划截止日期 |
| created_by | UUID | FK → users.id | 创建人 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

**枚举值（status）：**

| 值 | 说明 |
|----|------|
| `pending` | 待开始 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `cancelled` | 已取消 |

---

## 8. task_executions

**说明：** 测试任务中每条用例的执行记录。同一个用例可以在一个任务里被多次执行（重测）。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 执行记录唯一标识 |
| task_id | UUID | NOT NULL, FK → test_tasks.id | 所属测试任务 |
| test_case_id | UUID | NOT NULL, FK → test_cases.id | 对应测试用例 |
| executor_id | UUID | NOT NULL, FK → users.id | 执行人 |
| result | VARCHAR(10) | NOT NULL | 执行结果，见枚举值 |
| actual_result | TEXT | | 实际结果描述，失败时必填 |
| executed_at | TIMESTAMP | NOT NULL | 执行完成时间 |
| duration_seconds | INTEGER | NULLABLE | 执行耗时（秒） |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 记录创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

**枚举值（result）：**

| 值 | 说明 |
|----|------|
| `pass` | 通过 |
| `fail` | 失败，需创建缺陷 |
| `skip` | 跳过（如环境问题） |
| `blocked` | 被阻塞（依赖的功能未实现） |

---

## 9. defects

**说明：** 缺陷，整个系统的核心实体。包含完整的生命周期管理，支持三种来源（手工/自动化/性能）。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 缺陷唯一标识 |
| defect_no | VARCHAR(30) | UNIQUE NOT NULL | 缺陷编号，格式 `{APP_CODE}-{序号}`，如 `MALL-001` |
| app_id | UUID | NOT NULL, FK → applications.id | 所属应用 |
| title | VARCHAR(255) | NOT NULL | 缺陷标题，简洁描述问题 |
| description | TEXT | | 详细描述 |
| steps_to_reproduce | TEXT | | 复现步骤 |
| expected_result | TEXT | | 预期结果 |
| actual_result | TEXT | | 实际结果 |
| severity | VARCHAR(10) | NOT NULL DEFAULT 'medium' | 严重程度，见枚举值 |
| priority | VARCHAR(5) | NOT NULL DEFAULT 'P2' | 优先级，与 TestCase 相同枚举 |
| status | VARCHAR(20) | NOT NULL DEFAULT 'new' | 当前状态，见状态机 |
| found_version_id | UUID | NOT NULL, FK → versions.id | 发现版本 |
| fix_version_id | UUID | FK → versions.id, NULLABLE | 修复版本，NULL=未修复 |
| reporter_id | UUID | NOT NULL, FK → users.id | 提交人 |
| assignee_id | UUID | FK → users.id, NULLABLE | 当前负责人 |
| source | VARCHAR(20) | NOT NULL DEFAULT 'manual' | 来源，见枚举值 |
| source_run_id | UUID | NULLABLE | 来源执行记录 ID（automation_runs.id 或 perf_runs.id） |
| is_deleted | BOOLEAN | NOT NULL DEFAULT false | 软删除 |
| deleted_at | TIMESTAMP | NULLABLE | 软删除时间 |
| closed_at | TIMESTAMP | NULLABLE | 关闭时间 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

**枚举值（severity）：**

| 值 | 说明 | 示例 |
|----|------|------|
| `critical` | 致命，功能完全不可用 | 登录崩溃、数据丢失 |
| `high` | 严重，核心功能异常 | 支付失败、订单不创建 |
| `medium` | 一般，功能可用但有问题 | 筛选不准确、排序错误 |
| `low` | 轻微，体验问题 | 文案错别字、颜色偏差 |

**枚举值（source）：**

| 值 | 说明 |
|----|------|
| `manual` | 手工测试发现 |
| `automation` | 自动化执行失败自动创建 |
| `performance` | 性能测试 SLA 违反自动创建 |

**缺陷状态机：**

```
new ──→ assigned ──→ fixed ──→ verified ──→ closed
           │                      │
           ↓                      ↓
        rejected               reopened ──→ assigned
```

| 当前状态 | 允许流转到 | 操作人 |
|---------|-----------|-------|
| `new` | `assigned` | Admin / Tester |
| `assigned` | `fixed`, `rejected` | Developer（fixed），Admin/Tester（rejected）|
| `fixed` | `verified`, `reopened` | Tester（verified=验证通过，reopened=验证失败）|
| `verified` | `closed` | Admin / Tester |
| `rejected` | —（终态）| — |
| `closed` | `reopened` | Admin（重新激活）|
| `reopened` | `assigned` | Admin / Tester |

---

## 10. defect_comments

**说明：** 缺陷讨论评论，支持沟通协作。软删除，不物理删除。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 评论唯一标识 |
| defect_id | UUID | NOT NULL, FK → defects.id | 所属缺陷 |
| author_id | UUID | NOT NULL, FK → users.id | 评论人 |
| content | TEXT | NOT NULL | 评论内容，支持 Markdown |
| is_deleted | BOOLEAN | NOT NULL DEFAULT false | 软删除（仅自己和 Admin 可删） |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

---

## 11. defect_status_history

**说明：** 缺陷状态变更审计日志，只追加不修改，完整记录生命周期。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 记录唯一标识 |
| defect_id | UUID | NOT NULL, FK → defects.id | 所属缺陷 |
| from_status | VARCHAR(20) | NULLABLE | 变更前状态，NULL=首次创建 |
| to_status | VARCHAR(20) | NOT NULL | 变更后状态 |
| changed_by | UUID | NOT NULL, FK → users.id | 操作人 |
| comment | TEXT | NULLABLE | 附言，如"无法复现，拒绝" |
| changed_at | TIMESTAMP | NOT NULL DEFAULT now() | 变更时间 |

> **设计说明：** 此表只插入不修改，是审计日志，不加 `updated_at`。

---

## 12. test_case_defects

**说明：** 测试用例与缺陷的多对多关联表。一个用例可关联多个缺陷，一个缺陷可关联多个用例。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| test_case_id | UUID | PK, FK → test_cases.id | 测试用例 |
| defect_id | UUID | PK, FK → defects.id | 缺陷 |
| linked_by | UUID | FK → users.id | 关联操作人 |
| linked_at | TIMESTAMP | NOT NULL DEFAULT now() | 关联时间 |

---

## 13. automation_scripts

**说明：** 注册自动化测试脚本，记录脚本元信息和执行配置。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 脚本唯一标识 |
| app_id | UUID | NOT NULL, FK → applications.id | 所属应用 |
| name | VARCHAR(255) | NOT NULL | 脚本名称，如"登录模块回归测试" |
| description | TEXT | | 脚本说明 |
| script_type | VARCHAR(20) | NOT NULL | 脚本框架，见枚举值 |
| repo_url | VARCHAR(500) | NULLABLE | 代码仓库地址 |
| script_path | VARCHAR(500) | NULLABLE | 脚本入口路径，如 `tests/test_login.py` |
| is_active | BOOLEAN | NOT NULL DEFAULT true | 是否启用 |
| created_by | UUID | FK → users.id | 创建人 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

**枚举值（script_type）：**

| 值 | 说明 |
|----|------|
| `pytest` | Python pytest |
| `selenium` | Selenium WebDriver |
| `api` | 接口自动化（requests / httpx）|
| `robot` | Robot Framework |
| `playwright` | Playwright |

---

## 14. automation_runs

**说明：** 自动化脚本的每次执行记录，包含汇总统计数据。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 执行记录唯一标识 |
| script_id | UUID | NOT NULL, FK → automation_scripts.id | 所属脚本 |
| trigger_type | VARCHAR(20) | NOT NULL | 触发方式，见枚举值 |
| triggered_by | UUID | FK → users.id, NULLABLE | 触发人，定时触发时为 NULL |
| status | VARCHAR(20) | NOT NULL DEFAULT 'pending' | 执行状态，见枚举值 |
| total_cases | INTEGER | NOT NULL DEFAULT 0 | 总用例数 |
| passed | INTEGER | NOT NULL DEFAULT 0 | 通过数 |
| failed | INTEGER | NOT NULL DEFAULT 0 | 失败数 |
| skipped | INTEGER | NOT NULL DEFAULT 0 | 跳过数 |
| started_at | TIMESTAMP | NULLABLE | 开始时间 |
| finished_at | TIMESTAMP | NULLABLE | 结束时间 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 记录创建时间 |

**枚举值（trigger_type）：**

| 值 | 说明 |
|----|------|
| `manual` | 手动触发 |
| `scheduled` | 定时任务触发 |
| `daily` | 每日定时（Daily 报告来源）|

**枚举值（status）：**

| 值 | 说明 |
|----|------|
| `pending` | 等待执行 |
| `running` | 执行中 |
| `success` | 执行完成，全部通过 |
| `failed` | 执行完成，有用例失败 |
| `error` | 执行异常（脚本报错、环境问题）|

---

## 15. automation_run_details

**说明：** 自动化执行的单条用例结果，是 `automation_runs` 的明细。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 详情唯一标识 |
| run_id | UUID | NOT NULL, FK → automation_runs.id | 所属执行记录 |
| test_case_id | UUID | FK → test_cases.id, NULLABLE | 对应系统用例，NULL=脚本专有用例未在系统注册 |
| case_name | VARCHAR(255) | NOT NULL | 脚本内用例名（如 pytest 函数名 `test_login_success`）|
| result | VARCHAR(10) | NOT NULL | 执行结果，见枚举值 |
| error_message | TEXT | NULLABLE | 失败/异常的错误信息和堆栈 |
| duration_seconds | DECIMAL(8,2) | NULLABLE | 单用例执行耗时（秒）|
| auto_defect_id | UUID | FK → defects.id, NULLABLE | 失败时自动创建的缺陷 ID |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |

**枚举值（result）：**

| 值 | 说明 |
|----|------|
| `pass` | 通过 |
| `fail` | 断言失败 |
| `skip` | 被跳过（`@pytest.mark.skip`）|
| `error` | 异常报错（非断言失败，如环境问题）|

---

## 16. perf_scripts

**说明：** 性能测试脚本配置，包含 SLA 阈值定义，SLA 违反时自动创建缺陷。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 脚本唯一标识 |
| app_id | UUID | NOT NULL, FK → applications.id | 所属应用 |
| name | VARCHAR(255) | NOT NULL | 脚本名称，如"首页接口压测" |
| description | TEXT | | 脚本说明 |
| tool | VARCHAR(20) | NOT NULL | 压测工具，见枚举值 |
| script_path | VARCHAR(500) | NULLABLE | 脚本路径 |
| concurrent_users | INTEGER | NULLABLE | 并发用户数 |
| duration_seconds | INTEGER | NULLABLE | 测试持续时长（秒）|
| sla_tps | DECIMAL(10,2) | NULLABLE | TPS 最低阈值，低于则违反 |
| sla_avg_rt_ms | INTEGER | NULLABLE | 平均响应时间上限（毫秒）|
| sla_p95_rt_ms | INTEGER | NULLABLE | P95 响应时间上限（毫秒）|
| sla_error_rate | DECIMAL(5,2) | NULLABLE | 错误率上限（百分比，如 `1.00` = 1%）|
| is_active | BOOLEAN | NOT NULL DEFAULT true | 是否启用 |
| created_by | UUID | FK → users.id | 创建人 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL DEFAULT now() | 最后修改时间 |

**枚举值（tool）：**

| 值 | 说明 |
|----|------|
| `jmeter` | Apache JMeter |
| `locust` | Locust（Python）|
| `k6` | Grafana k6 |
| `gatling` | Gatling（Scala）|

---

## 17. perf_runs

**说明：** 性能测试执行记录，存储关键指标数据，SLA 违反时自动创建缺陷。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 执行记录唯一标识 |
| script_id | UUID | NOT NULL, FK → perf_scripts.id | 所属脚本 |
| trigger_type | VARCHAR(20) | NOT NULL | 触发方式：`manual` / `scheduled` |
| triggered_by | UUID | FK → users.id, NULLABLE | 触发人 |
| status | VARCHAR(20) | NOT NULL DEFAULT 'pending' | 执行状态，同 automation_runs |
| tps | DECIMAL(10,2) | NULLABLE | 实测 TPS（每秒事务数）|
| avg_rt_ms | INTEGER | NULLABLE | 实测平均响应时间（毫秒）|
| p95_rt_ms | INTEGER | NULLABLE | 实测 P95 响应时间（毫秒）|
| p99_rt_ms | INTEGER | NULLABLE | 实测 P99 响应时间（毫秒）|
| error_rate | DECIMAL(5,2) | NULLABLE | 实测错误率（百分比）|
| max_concurrent | INTEGER | NULLABLE | 实际最大并发数 |
| sla_violated | BOOLEAN | NOT NULL DEFAULT false | 是否违反 SLA |
| auto_defect_id | UUID | FK → defects.id, NULLABLE | SLA 违反时自动创建的缺陷 |
| report_url | VARCHAR(500) | NULLABLE | 详细报告文件/链接地址 |
| started_at | TIMESTAMP | NULLABLE | 开始时间 |
| finished_at | TIMESTAMP | NULLABLE | 结束时间 |
| created_at | TIMESTAMP | NOT NULL DEFAULT now() | 创建时间 |

---

## 附录：索引建议

```sql
-- 高频查询场景的索引
CREATE INDEX idx_defects_app_status    ON defects(app_id, status) WHERE is_deleted = false;
CREATE INDEX idx_defects_assignee      ON defects(assignee_id) WHERE status NOT IN ('closed','rejected');
CREATE INDEX idx_test_cases_app        ON test_cases(app_id, category) WHERE is_deleted = false;
CREATE INDEX idx_task_executions_task  ON task_executions(task_id, result);
CREATE INDEX idx_automation_runs_script ON automation_runs(script_id, trigger_type, started_at DESC);
CREATE INDEX idx_perf_runs_script      ON perf_runs(script_id, started_at DESC);
CREATE INDEX idx_defect_history_defect ON defect_status_history(defect_id, changed_at);
```

## 附录：缺陷编号生成策略

```python
# 方案一：数据库序列（推荐，不会重号）
# 每个 Application 维护一个序列
CREATE SEQUENCE defect_seq_{app_code};
defect_no = f"{app_code}-{nextval(defect_seq)}"

# 方案二：应用层计数（简单，Phase 1 可用）
# SELECT COUNT(*) FROM defects WHERE app_id = ? → 加 1 → 格式化
defect_no = f"{app_code}-{count + 1:04d}"  # 如 MALL-0001
```
