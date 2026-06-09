# test-center 设计文档

日期：2026-06-05
作者：Yang Li
阶段：Phase 1（Python 后端工程化基础）

---

## 1. 项目背景与目标

### 定位

test-center 是一个类 TAPD 的测试管理平台，覆盖功能测试全流程，是10年测试经验的技术化沉淀。

### Phase 1 目标

用 FastAPI 交付一个生产级 REST API 服务，具备：
- 完整的认证与 RBAC 权限控制（JWT）
- 关系型数据库建模与迁移（PostgreSQL + SQLAlchemy 2.0 + Alembic）
- 核心业务流程可跑通（应用→版本→用例→任务→执行→缺陷→流转）
- 生产级代码质量（统一响应、全局异常、pytest 测试覆盖）
- 容器化（Docker Compose）

### Phase 1 范围（第一批：功能测试核心）

覆盖 12 张表（8 个核心实体表 + 3 张关联/历史表 + roles），自动化/性能测试模块留第二批：

| 模块 | 表 |
|------|---|
| 用户权限 | users, roles, user_roles |
| 应用管理 | applications, versions |
| 测试用例 | test_cases |
| 测试执行 | test_tasks, task_executions |
| 缺陷管理 | defects, defect_comments, defect_status_history, test_case_defects |

前端：不做，使用 FastAPI 自动生成的 Swagger UI（`/docs`）。

---

## 2. 项目结构

混合方案：业务逻辑按模块纵向切，SQLAlchemy 模型统一横放，基础设施放 `core/`。

```
test-center/
├── app/
│   ├── main.py                      ← FastAPI 实例、注册路由、全局异常 handler
│   │
│   ├── core/                        ← 共享基础设施（无业务逻辑）
│   │   ├── config.py                ← 环境变量（pydantic-settings）
│   │   ├── database.py              ← engine、SessionLocal、get_db
│   │   ├── security.py              ← JWT 生成/验证、bcrypt 密码哈希
│   │   ├── deps.py                  ← 依赖注入：get_current_user、require_role
│   │   ├── exceptions.py            ← 自定义异常类
│   │   └── responses.py             ← 统一响应格式
│   │
│   ├── models/                      ← 所有 SQLAlchemy 模型集中（避免循环导入）
│   │   ├── base.py                  ← Base、TimestampMixin
│   │   ├── user.py                  ← User、Role、UserRole
│   │   ├── application.py           ← Application
│   │   ├── version.py               ← Version
│   │   ├── test_case.py             ← TestCase
│   │   ├── test_task.py             ← TestTask
│   │   ├── execution.py             ← TaskExecution
│   │   ├── defect.py                ← Defect、DefectComment、DefectStatusHistory
│   │   └── associations.py          ← test_case_defects 多对多中间表
│   │
│   ├── auth/
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── application/
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── test_case/
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── test_task/
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   └── defect/
│       ├── router.py
│       ├── service.py
│       ├── schemas.py
│       └── state_machine.py         ← 状态流转规则（纯业务逻辑，独立可测）
│
├── tests/
│   ├── conftest.py                  ← test_db、client、预置 fixtures
│   ├── test_auth.py
│   ├── test_applications.py
│   ├── test_test_cases.py
│   ├── test_test_tasks.py
│   └── test_defects.py              ← 重点：状态机全路径测试
│
├── alembic/
│   ├── env.py
│   └── versions/
│
├── alembic.ini
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml                   ← ruff、black 配置
```

---

## 3. API 设计

### 统一约定

- 前缀：`/api/v1`
- 认证：除登录/注册外，所有接口需 `Authorization: Bearer <token>`
- 分页：`?page=1&page_size=20`
- 软删除：DELETE 接口均为逻辑删除，不物理删除

### 统一响应格式

```json
// 成功
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}

// 失败
{
  "success": false,
  "error": {
    "code": "DEFECT_NOT_FOUND",
    "message": "缺陷不存在"
  }
}
```

### 认证 `/api/v1/auth`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/register` | 注册 | 公开 |
| POST | `/login` | 登录，返回 JWT | 公开 |
| GET | `/me` | 获取当前用户信息 | 登录 |

### 应用管理 `/api/v1/apps`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/apps` | 应用列表（分页） | 登录 |
| POST | `/apps` | 创建应用 | Admin |
| GET | `/apps/{app_id}` | 应用详情 | 登录 |
| PUT | `/apps/{app_id}` | 修改应用 | Admin |
| DELETE | `/apps/{app_id}` | 归档应用（软删除） | Admin |
| GET | `/apps/{app_id}/versions` | 版本列表 | 登录 |
| POST | `/apps/{app_id}/versions` | 创建版本 | Admin/Tester |

### 测试用例 `/api/v1`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/apps/{app_id}/test-cases` | 用例列表（分页+过滤） | 登录 |
| POST | `/apps/{app_id}/test-cases` | 创建用例 | Tester |
| GET | `/test-cases/{id}` | 用例详情 | 登录 |
| PUT | `/test-cases/{id}` | 修改用例 | Tester |
| DELETE | `/test-cases/{id}` | 软删除用例 | Tester/Admin |

过滤参数：`?category=登录模块&priority=P0&is_automated=true`

### 测试任务 & 执行 `/api/v1`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/apps/{app_id}/test-tasks` | 任务列表 | 登录 |
| POST | `/apps/{app_id}/test-tasks` | 创建任务 | Tester/Admin |
| GET | `/test-tasks/{task_id}` | 任务详情 | 登录 |
| PUT | `/test-tasks/{task_id}` | 修改任务 | Tester/Admin |
| GET | `/test-tasks/{task_id}/executions` | 执行记录列表 | 登录 |
| POST | `/test-tasks/{task_id}/executions` | 提交执行结果 | Tester |
| PUT | `/executions/{id}` | 修改执行结果 | Tester |

### 缺陷 `/api/v1`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/apps/{app_id}/defects` | 缺陷列表（分页+过滤） | 登录 |
| POST | `/apps/{app_id}/defects` | 创建缺陷 | Tester/Admin |
| GET | `/defects/{id}` | 缺陷详情（含评论和历史） | 登录 |
| PUT | `/defects/{id}` | 修改缺陷基本信息 | Tester/Admin |
| DELETE | `/defects/{id}` | 软删除 | Admin |
| POST | `/defects/{id}/transitions` | 状态流转（核心动作） | 角色限制（见下） |
| POST | `/defects/{id}/comments` | 添加评论 | 登录 |
| GET | `/defects/{id}/history` | 状态变更历史 | 登录 |

过滤参数：`?status=new&severity=critical&assignee_id=xxx&source=automation`

**状态流转请求体：**
```json
{
  "to_status": "assigned",
  "assignee_id": "uuid-xxx",
  "comment": "指派给张三处理"
}
```

**状态流转权限矩阵（"或"关系，拥有其中一个角色即可）：**

| 流转 | 允许角色 |
|------|---------|
| new → assigned | Admin 或 Tester |
| assigned → fixed | Developer |
| assigned → rejected | Admin 或 Tester |
| fixed → verified | Tester |
| fixed → reopened | Tester |
| verified → closed | Admin 或 Tester |
| closed → reopened | Admin |
| reopened → assigned | Admin 或 Tester |

---

## 4. 请求数据流

```
HTTP Request
    │
    ▼
main.py (FastAPI 实例)
    │  全局异常 handler、注册所有 router
    │
    ▼
router.py  ←── core/deps.py (get_current_user, require_role)
    │  职责：参数解析、权限校验、调用 service、返回响应
    │  不含任何业务逻辑
    │
    ▼
service.py  ←── defect/state_machine.py（缺陷模块）
    │  职责：业务规则、状态校验、跨模型操作
    │  直接使用 db session 操作 SQLAlchemy
    │
    ▼
SQLAlchemy ORM (2.0 现代语法)
    │
    ▼
PostgreSQL
```

> **说明：** Phase 1 不单独抽 repository 层，router→service→ORM 三层已体现分层思维，repository 层在 Phase 3 拆微服务时引入更自然。

---

## 5. 技术选型

| 类别 | 选型 |
|------|------|
| Python | 3.11+ |
| Web 框架 | FastAPI 0.111+ |
| ORM | SQLAlchemy 2.0（现代 `select()` 语法）|
| 迁移 | Alembic |
| 环境配置 | pydantic-settings 2.x |
| JWT | python-jose 3.x |
| 密码哈希 | passlib[bcrypt] |
| 测试 | pytest + httpx |
| Lint | ruff（替代 flake8 + isort）|
| 格式化 | black |
| 容器 | Docker Compose（api + db + redis）|

---

## 6. 错误处理

```python
# core/exceptions.py
class NotFoundError(Exception):    # → 404
class ForbiddenError(Exception):   # → 403
class BusinessError(Exception):    # → 400，业务规则违反（如非法状态流转）
class ConflictError(Exception):    # → 409，唯一约束冲突（如 app code 重复）
```

- `main.py` 注册全局 exception handler，统一转成标准响应格式
- router 和 service 中直接 `raise`，不写 `try/except`
- SQLAlchemy 异常在 `main.py` 统一捕获，不透传数据库错误信息给客户端

---

## 7. 测试策略

```
tests/
├── conftest.py
│   ├── test_db     ← 每个测试用独立事务，测完自动回滚，不污染数据
│   ├── client      ← httpx AsyncClient
│   └── fixtures    ← admin_user、tester_user、developer_user、test_app
│
├── test_auth.py          ← 注册、登录、token 验证、无效 token
├── test_applications.py  ← CRUD、权限（非 Admin 创建 → 403）
├── test_test_cases.py    ← CRUD、分页、过滤
├── test_test_tasks.py    ← 任务创建、执行提交、结果修改
└── test_defects.py       ← 状态机全路径（合法流转 + 非法跳转 → 400）
                             RBAC（Developer 关闭缺陷 → 403）
                             软删除（删后查询不返回）
```

**测试重点：**
- 缺陷状态机：每条合法路径 + 每条非法跳转均有测试用例
- RBAC：各角色越权操作均返回 403
- 软删除：删除后列表查询不返回；详情查询返回 404

---

## 8. Docker Compose

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    depends_on: [db, redis]
    env_file: .env

  db:
    image: postgres:15
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: test_center
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    # Phase 1 占位，Phase 2 Week 3 正式使用
```

---

## 9. 实现顺序（Phase 1）

按此顺序实现，每步都有可运行的中间状态：

1. 项目骨架 + `core/`（config、database、exceptions、responses）
2. SQLAlchemy 模型 + Alembic 初始迁移（8 张核心表）
3. 认证模块（注册、登录、JWT、`get_current_user`）
4. Application + Version 模块（最简单，验证分层结构）
5. TestCase 模块（带分页过滤）
6. TestTask + TaskExecution 模块
7. Defect 模块（状态机、评论、历史）
8. pytest 测试补全
9. Dockerfile + docker-compose，本地跑通
