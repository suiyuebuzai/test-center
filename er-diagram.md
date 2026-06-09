# test-center ER 图

日期：2026-06-05

> 使用 Mermaid erDiagram 语法，可在 Obsidian / VS Code (Markdown Preview Mermaid) / GitHub 直接渲染。

---

## 完整 ER 图

```mermaid
erDiagram

    %% ──────────────────────────────
    %% 用户 & 权限
    %% ──────────────────────────────
    users {
        uuid id PK
        varchar username
        varchar email
        varchar hashed_password
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    roles {
        smallint id PK
        varchar name
        varchar description
    }

    user_roles {
        uuid user_id PK,FK
        smallint role_id PK,FK
        uuid app_id PK,FK "NULL=全局角色"
        timestamp granted_at
        uuid granted_by FK
    }

    %% ──────────────────────────────
    %% 应用 & 版本
    %% ──────────────────────────────
    applications {
        uuid id PK
        varchar name
        varchar code "短码，缺陷编号前缀"
        text description
        boolean is_active
        boolean is_deleted
        timestamp deleted_at
        uuid created_by FK
        timestamp created_at
        timestamp updated_at
    }

    versions {
        uuid id PK
        uuid app_id FK
        varchar name "e.g. v1.2.0"
        text description
        varchar status "planning/testing/released/archived"
        date release_date
        uuid created_by FK
        timestamp created_at
        timestamp updated_at
    }

    %% ──────────────────────────────
    %% 测试用例
    %% ──────────────────────────────
    test_cases {
        uuid id PK
        uuid app_id FK
        varchar title
        text description
        text preconditions
        jsonb steps "步骤数组"
        text expected_result
        varchar category "功能分类"
        varchar priority "P0/P1/P2/P3"
        varchar case_type "functional/performance/security/regression"
        boolean is_automated
        boolean is_deleted
        timestamp deleted_at
        uuid created_by FK
        uuid updated_by FK
        timestamp created_at
        timestamp updated_at
    }

    %% ──────────────────────────────
    %% 测试任务 & 执行
    %% ──────────────────────────────
    test_tasks {
        uuid id PK
        uuid app_id FK
        uuid version_id FK
        varchar name
        text description
        varchar status "pending/in_progress/completed/cancelled"
        uuid assignee_id FK
        date start_date
        date due_date
        uuid created_by FK
        timestamp created_at
        timestamp updated_at
    }

    task_executions {
        uuid id PK
        uuid task_id FK
        uuid test_case_id FK
        uuid executor_id FK
        varchar result "pass/fail/skip/blocked"
        text actual_result
        timestamp executed_at
        integer duration_seconds
        timestamp created_at
        timestamp updated_at
    }

    %% ──────────────────────────────
    %% 缺陷（核心实体）
    %% ──────────────────────────────
    defects {
        uuid id PK
        varchar defect_no "APP-001，唯一"
        uuid app_id FK
        varchar title
        text description
        text steps_to_reproduce
        text expected_result
        text actual_result
        varchar severity "critical/high/medium/low"
        varchar priority "P0/P1/P2/P3"
        varchar status "new/assigned/fixed/verified/closed/rejected/reopened"
        uuid found_version_id FK
        uuid fix_version_id FK "nullable"
        uuid reporter_id FK
        uuid assignee_id FK "nullable"
        varchar source "manual/automation/performance"
        uuid source_run_id "nullable，关联执行记录"
        boolean is_deleted
        timestamp deleted_at
        timestamp closed_at
        timestamp created_at
        timestamp updated_at
    }

    defect_comments {
        uuid id PK
        uuid defect_id FK
        uuid author_id FK
        text content
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }

    defect_status_history {
        uuid id PK
        uuid defect_id FK
        varchar from_status "nullable，新建时为空"
        varchar to_status
        uuid changed_by FK
        text comment
        timestamp changed_at
    }

    test_case_defects {
        uuid test_case_id PK,FK
        uuid defect_id PK,FK
        uuid linked_by FK
        timestamp linked_at
    }

    %% ──────────────────────────────
    %% 自动化脚本
    %% ──────────────────────────────
    automation_scripts {
        uuid id PK
        uuid app_id FK
        varchar name
        text description
        varchar script_type "pytest/selenium/api/robot"
        varchar repo_url
        varchar script_path
        boolean is_active
        uuid created_by FK
        timestamp created_at
        timestamp updated_at
    }

    automation_runs {
        uuid id PK
        uuid script_id FK
        varchar trigger_type "manual/scheduled/daily"
        uuid triggered_by FK "nullable"
        varchar status "pending/running/success/failed/error"
        integer total_cases
        integer passed
        integer failed
        integer skipped
        timestamp started_at
        timestamp finished_at
        timestamp created_at
    }

    automation_run_details {
        uuid id PK
        uuid run_id FK
        uuid test_case_id FK "nullable"
        varchar case_name "脚本内用例名"
        varchar result "pass/fail/skip/error"
        text error_message
        decimal duration_seconds
        uuid auto_defect_id FK "nullable，失败自动创建的缺陷"
        timestamp created_at
    }

    %% ──────────────────────────────
    %% 性能测试
    %% ──────────────────────────────
    perf_scripts {
        uuid id PK
        uuid app_id FK
        varchar name
        text description
        varchar tool "jmeter/locust/k6/gatling"
        varchar script_path
        integer concurrent_users
        integer duration_seconds
        decimal sla_tps "TPS 阈值"
        integer sla_avg_rt_ms "平均RT阈值(ms)"
        integer sla_p95_rt_ms "P95 RT阈值(ms)"
        decimal sla_error_rate "错误率阈值(%)"
        boolean is_active
        uuid created_by FK
        timestamp created_at
        timestamp updated_at
    }

    perf_runs {
        uuid id PK
        uuid script_id FK
        varchar trigger_type "manual/scheduled"
        uuid triggered_by FK "nullable"
        varchar status "pending/running/success/failed/error"
        decimal tps
        integer avg_rt_ms
        integer p95_rt_ms
        integer p99_rt_ms
        decimal error_rate
        integer max_concurrent
        boolean sla_violated
        uuid auto_defect_id FK "nullable，SLA违反时自动创建"
        varchar report_url
        timestamp started_at
        timestamp finished_at
        timestamp created_at
    }

    %% ══════════════════════════════════
    %% 关系定义
    %% ══════════════════════════════════

    %% 用户 & 权限
    users ||--o{ user_roles : "被授予角色"
    roles ||--o{ user_roles : "授予给用户"
    applications ||--o{ user_roles : "应用级角色(可NULL)"

    %% 应用 & 版本
    users ||--o{ applications : "creates"
    applications ||--|{ versions : "包含多个版本"

    %% 测试用例
    applications ||--o{ test_cases : "包含用例"

    %% 测试任务
    applications ||--o{ test_tasks : "所属应用"
    versions ||--o{ test_tasks : "所属版本"
    users ||--o{ test_tasks : "负责人"

    %% 任务执行
    test_tasks ||--|{ task_executions : "包含执行记录"
    test_cases ||--o{ task_executions : "被执行"
    users ||--o{ task_executions : "执行人"

    %% 缺陷
    applications ||--o{ defects : "所属应用"
    versions ||--o{ defects : "发现版本"
    versions ||--o{ defects : "修复版本"
    users ||--o{ defects : "reporter"
    users ||--o{ defects : "assignee"

    %% 缺陷评论 & 历史
    defects ||--o{ defect_comments : "包含评论"
    defects ||--o{ defect_status_history : "状态变更历史"
    users ||--o{ defect_comments : "评论人"
    users ||--o{ defect_status_history : "变更人"

    %% 用例-缺陷 多对多
    test_cases }o--o{ defects : "test_case_defects"

    %% 自动化
    applications ||--o{ automation_scripts : "所属应用"
    automation_scripts ||--o{ automation_runs : "执行记录"
    automation_runs ||--o{ automation_run_details : "单用例结果"
    test_cases ||--o{ automation_run_details : "对应用例(可NULL)"
    defects ||--o{ automation_run_details : "自动创建的缺陷"

    %% 性能
    applications ||--o{ perf_scripts : "所属应用"
    perf_scripts ||--o{ perf_runs : "执行记录"
    defects ||--o{ perf_runs : "SLA违反自动创建的缺陷"
```

---

## 关键关系说明

### 1. 缺陷来源（source 字段）

```
task_executions (result=fail)  →  手工创建  →  defects (source=manual)
automation_run_details (fail)  →  自动创建  →  defects (source=automation)
perf_runs (sla_violated=true)  →  自动创建  →  defects (source=performance)
```

### 2. 用例与缺陷的多对多

```
一个 TestCase 可以关联多个 Defect（不同版本的相同 Bug）
一个 Defect 可以关联多个 TestCase（多条用例都触发了同一 Bug）
```

### 3. 角色权限范围

```
user_roles.app_id = NULL  →  全局角色（对所有应用生效）
user_roles.app_id = xxx   →  应用级角色（只对该应用生效）
```

### 4. 版本在缺陷中的两个外键

```
defects.found_version_id  →  在哪个版本发现的（必填）
defects.fix_version_id    →  在哪个版本修复的（NULL=未修复）
```
