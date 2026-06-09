# test-center 项目进度 & 学习记录

> 最后更新：2026-06-09

---

## 当前状态：Phase 1 ✅ 已完成 + 前端 ✅ 已完成 + Codespaces 部署 ✅ 已完成

**39/39 测试全部通过**（auth×6, applications×5, test_cases×3, test_tasks×3, state_machine×16, defects×6）

---

## Phase 1 完成清单

| 任务 | 内容 | 状态 |
|------|------|------|
| Task 1 | 项目骨架（requirements.txt, pyproject.toml, main.py, __init__.py） | ✅ |
| Task 2 | 核心基础设施（exceptions, database, responses, security, deps, .env） | ✅ |
| Task 3 | SQLAlchemy 数据模型（12 张表） | ✅ |
| Task 4 | Alembic 迁移配置 + 建表（initial_schema） | ✅ |
| Task 5 | 认证模块（注册/登录/JWT/get_current_user） | ✅ |
| Task 6 | 应用 & 版本模块（CRUD + 分页 + RBAC） | ✅ |
| Task 7 | 测试用例模块（CRUD + 分页过滤 + 软删除） | ✅ |
| Task 8 | 测试任务 & 执行模块 | ✅ |
| Task 9 | 缺陷状态机（16 个单元测试） | ✅ |
| Task 10 | 缺陷模块（状态机 + 评论 + 历史记录） | ✅ |
| Task 11 | Docker 配置（Dockerfile + docker-compose） | ✅ |

---

## 项目全景概览

### 1. 项目定位

测试管理平台（类 TAPD），覆盖手工测试 → 缺陷追踪 → 自动化/性能测试的完整闭环。

### 2. 技术栈

| 层次 | 技术 |
|------|------|
| Web 框架 | FastAPI 0.111 |
| ORM | SQLAlchemy 2.0（Mapped 声明式） |
| 数据库 | PostgreSQL 15 |
| 数据库迁移 | Alembic |
| 认证 | JWT（python-jose）+ bcrypt 密码哈希 |
| 配置管理 | pydantic-settings（读取 .env） |
| 测试 | pytest + httpx AsyncClient |
| 容器化 | Docker + docker-compose（API + PostgreSQL + Redis） |

### 3. 目录结构

```
app/
├── main.py                  # 应用入口：注册路由 + 全局异常处理器
├── core/
│   ├── config.py            # Settings（pydantic-settings 读取 .env）
│   ├── database.py          # SQLAlchemy engine + get_db 依赖
│   ├── deps.py              # get_current_user / require_roles 依赖
│   ├── exceptions.py        # NotFoundError / ForbiddenError / BusinessError / ConflictError
│   ├── responses.py         # success() / created() 统一响应格式
│   └── security.py          # hash_password / verify_password / JWT 签发&解码
├── models/
│   ├── base.py              # Base + TimestampMixin + SoftDeleteMixin
│   ├── user.py              # User / Role / UserRole
│   ├── application.py       # Application / Version
│   ├── test_case.py         # TestCase
│   ├── test_task.py         # TestTask / TaskExecution
│   ├── defect.py            # Defect / DefectComment / DefectStatusHistory
│   ├── execution.py         # （任务执行相关）
│   └── associations.py      # test_case_defects 多对多中间表
├── auth/                    # 注册 / 登录 / JWT
├── application/             # 应用 & 版本 CRUD
├── test_case/               # 测试用例 CRUD + 软删除
├── test_task/               # 测试任务 & 执行记录
└── defect/
    ├── state_machine.py     # 缺陷状态流转规则 + 角色权限
    ├── service.py
    ├── router.py
    └── schemas.py
tests/
├── conftest.py              # 测试 DB 初始化 / 清表 / client fixture
├── test_auth.py
├── test_applications.py
├── test_test_cases.py
├── test_test_tasks.py
├── test_state_machine.py
└── test_defects.py
alembic/
└── versions/0347343374b3_initial_schema.py
```

### 4. 核心设计模式

#### 4.1 分层架构（每个业务模块）
```
router.py   → 接收 HTTP 请求，调用 service，返回统一响应
service.py  → 业务逻辑，操作 ORM 模型
schemas.py  → Pydantic 模型（请求体 / 响应体）
```

#### 4.2 统一响应格式
```json
// 成功
{"success": true, "data": {...}, "message": "操作成功"}
// 失败
{"success": false, "error": {"code": "NOT_FOUND", "message": "资源不存在"}}
```

#### 4.3 自定义异常体系
```
NotFoundError   → 404
ForbiddenError  → 403
BusinessError   → 400（含 code + message）
ConflictError   → 409
```

#### 4.4 JWT 认证流程
```
POST /auth/register → 创建用户 + 分配角色
POST /auth/login    → 验证密码 → 签发 JWT
其他接口            → HTTPBearer 提取 Token → decode → get_current_user
```

#### 4.5 RBAC 角色控制
- 4 个预置角色：`admin` / `tester` / `developer` / `readonly`
- `require_roles("admin", "tester")` 工厂依赖，路由级鉴权
- `UserRole` 支持全局角色（`app_id=NULL`）和应用级角色

#### 4.6 缺陷状态机
```
new → assigned → fixed → verified → closed
             ↘ rejected（终态）
fixed → reopened → assigned
closed → reopened → assigned
```
每条流转绑定允许角色，违规时抛 `BusinessError`。

### 5. 数据库表清单（12 张）

| 表名 | 说明 |
|------|------|
| roles | 角色字典 |
| users | 用户（UUID 主键） |
| user_roles | 用户角色关联（支持应用级） |
| applications | 被测应用 |
| versions | 应用版本 |
| test_cases | 测试用例（软删除 + JSONB steps） |
| test_tasks | 测试任务 |
| task_executions | 测试执行记录 |
| defects | 缺陷（状态机 + source 来源标记） |
| defect_comments | 缺陷评论 |
| defect_status_history | 缺陷状态变更历史 |
| test_case_defects | 用例↔缺陷多对多 |

### 6. 测试策略

- `conftest.py`：session 级建表 + 预置 roles；每个测试后 TRUNCATE 清数据
- `client` fixture：`AsyncClient` + 覆盖 `get_db` 依赖注入测试数据库
- 测试库与主库隔离：`test_center_test` vs `test_center`

### 7. 环境说明

| 项目 | 值 |
|------|----|
| Python | `C:\1AI\.pvenv`（Python 3.13.0） |
| 运行命令 | `C:\1AI\.pvenv\Scripts\python.exe` |
| PostgreSQL | localhost:5432，user=postgres，password=root |
| 主库 | test_center |
| 测试库 | test_center_test |

### 8. 关键修复记录

1. **bcrypt 兼容性** — passlib 1.7.4 与 bcrypt 5.0.0 不兼容，`security.py` 改为直接调用 `bcrypt` 库
2. **数据库需手动创建** — `test_center` / `test_center_test` 需手动建库
3. **缺陷状态历史计数** — 创建缺陷时写入初始历史（from_status=None），首次流转后历史条数为 2
4. **UUID 序列化** — `model_dump()` 需改为 `model_dump(mode="json")` 才能序列化 UUID

---

## 前端完成清单（2026-06-09）

### 技术栈

| 层次 | 技术 |
|------|------|
| 框架 | React 18 + TypeScript |
| UI 组件库 | Ant Design 5 |
| 构建工具 | Vite |
| 路由 | React Router v6 |
| 数据请求 | Axios + TanStack React Query v5 |
| 测试 | Vitest + Testing Library |

### 目录结构

```
frontend/src/
├── api/
│   ├── client.ts          # axios 实例（JWT 拦截器 + 401 自动跳登录）
│   ├── apps.ts            # 应用 & 版本接口
│   ├── auth.ts            # 登录注册接口
│   ├── defects.ts         # 缺陷接口
│   ├── testCases.ts       # 测试用例接口
│   └── testTasks.ts       # 测试任务 & 执行记录接口
├── hooks/
│   ├── useApps.ts
│   ├── useDefects.ts
│   ├── useTestCases.ts
│   └── useTestTasks.ts
├── context/
│   └── AuthContext.tsx    # 登录态 + user + roles + hasRole()
├── components/
│   ├── AppLayout/         # Header（应用切换）+ Sider（导航菜单）
│   └── PrivateRoute.tsx   # 未登录重定向到 /login
└── pages/
    ├── Login/             # 登录表单
    ├── AppList/           # 应用卡片列表 + 新建应用
    ├── TestCases/         # 用例表格 + 详情抽屉 + 新建/删除
    ├── Defects/
    │   ├── index.tsx      # 缺陷列表 + 过滤 + 新建
    │   └── DefectDetail.tsx  # 缺陷详情 + 状态流转 + 评论
    └── TestTasks/
        ├── index.tsx      # 任务列表 + 新建任务
        └── TestTaskDetail.tsx  # 任务详情 + 执行记录列表 + 添加执行
```

### 路由清单

| 路由 | 页面 |
|------|------|
| `/login` | 登录 |
| `/apps` | 应用列表 |
| `/apps/:appId/test-cases` | 测试用例 |
| `/apps/:appId/defects` | 缺陷列表 |
| `/apps/:appId/defects/:defectId` | 缺陷详情 |
| `/apps/:appId/test-tasks` | 测试任务列表 |
| `/apps/:appId/test-tasks/:taskId` | 测试任务详情 |

### 本地运行方式

```bash
# 1. 建表（首次）
source /c/1AI/.pvenv/Scripts/activate
cd <项目根目录>
alembic upgrade head

# 2. 插入角色数据（首次，migration 不自动 seed）
psql -U postgres -d test_center -c "INSERT INTO roles (id, name, description) VALUES (1, 'admin', '管理员'), (2, 'tester', '测试人员'), (3, 'developer', '开发人员'), (4, 'readonly', '只读用户') ON CONFLICT DO NOTHING;"

# 3. 启动后端
uvicorn app.main:app --reload --port 8000

# 4. 启动前端（另开终端）
cd frontend && npm run dev
# 访问 http://localhost:5173
```

### 已知遗留问题

| 问题 | 位置 | 说明 |
|------|------|------|
| TS 类型错误 | `api/defects.ts` | `Defect` 接口缺少 `description` / `steps_to_reproduce` 字段 |
| TS 类型错误 | `api/client.test.ts` | axios interceptors.handlers 类型判断 |
| 显示 UUID | `DefectDetail.tsx` | assignee、found_version 显示裸 UUID 而非名称 |
| 显示 UUID | `TestTaskDetail.tsx` | test_case_id 显示裸 UUID 而非用例名称 |

---

## GitHub Codespaces 部署（2026-06-09）✅

### 部署目标
在 GitHub Codespaces 云端环境中运行完整项目（前端 + 后端 + PostgreSQL），无需本地安装任何依赖。

### 仓库地址
`https://github.com/suiyuebuzai/test-center`

### 关键配置文件

#### `.devcontainer/devcontainer.json`
```json
{
  "name": "Test Center Dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": { "version": "20" }
  },
  "forwardPorts": [8000, 5173],
  "portsAttributes": {
    "5173": { "label": "Frontend", "onAutoForward": "openBrowser" }
  },
  "postCreateCommand": "bash .devcontainer/setup.sh",
  "remoteUser": "root"
}
```

#### `.devcontainer/setup.sh`
容器创建时自动执行，完成 PostgreSQL 安装、数据库初始化、依赖安装：
```bash
apt-get install -y postgresql postgresql-contrib
service postgresql start
runuser -u postgres -- psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
runuser -u postgres -- createdb test_center
pip install -r requirements.txt
alembic upgrade head
cd frontend && npm install
```

### 启动方式
Codespace 初始化完成后，开两个终端：
```bash
# 终端 1 — 后端
uvicorn app.main:app --reload --port 8000

# 终端 2 — 前端
cd frontend && npm run dev -- --host
```

访问前端：Codespaces 自动弹出 5173 端口的公网链接（格式如 `https://<name>-5173.app.github.dev`）

### 踩坑记录

| 坑 | 原因 | 解决方案 |
|----|------|---------|
| `postgres:1` feature 报错 | Codespaces 无法从 `ghcr.io` 拉取 feature | 改为 `apt-get install postgresql` |
| `sudo` 要求输入密码 | recovery 容器无 NOPASSWD 配置 | `remoteUser` 改为 `root` |
| 注册接口 500 错误 | `roles` 表为空，migration 不 seed 数据 | 新增 `a1b2c3d4e5f6_seed_roles.py` 迁移 |
| 前端 Codespaces 访问不到 | Vite 默认只监听 localhost | `vite.config.ts` 加 `host: true`，启动时加 `-- --host` |

### Docker 单容器方案（前后端合一）

采用多阶段构建，一个镜像包含前端和后端：
- Stage 1：Node 构建前端 → `dist/`
- Stage 2：Python 镜像复制 `dist/`，FastAPI 用 `StaticFiles` 托管静态文件

```bash
docker compose up --build  # 访问 http://localhost:8000
```

---

## Phase 2 待做内容

- [ ] 自动化脚本模块（automation_scripts, automation_runs, automation_run_details）
- [ ] 性能测试模块（perf_scripts, perf_runs）
- [ ] 增强 RBAC（应用级角色、用户角色管理接口）
- [ ] 报告 API（测试通过率、缺陷趋势统计）
- [x] Docker 单容器方案（多阶段构建，前后端合一）✅ 2026-06-09
- [x] GitHub Codespaces 部署 ✅ 2026-06-09
- [ ] Docker Compose 多容器（Nginx + 独立前端容器）
- [ ] GitHub Actions CI/CD 流水线
- [ ] 云服务器部署（阿里云/AWS + Nginx + HTTPS）

---

## 学习问答记录

> 以下按时间顺序记录问答，每条格式：问题 → 要点总结

<!-- 问答记录从这里开始 -->

### Q1：models 里为什么要单独建一个 associations.py？

**核心原因：避免循环导入 + 这张表属于中间地带**

`test_case_defects` 是 `TestCase` ↔ `Defect` 的多对多中间表。
- `test_case.py` 引用它，`defect.py` 也引用它
- 如果放在任何一方，另一方导入时会形成循环依赖
- 放在独立文件，两边都单向导入，循环消失

此外，中间表本身是 SQLAlchemy Core 的 `Table` 对象（不是 ORM class），不归属任何一个业务模块，单独放语义更清晰。

> 规律：多对多中间表 + 有额外字段（linked_by、linked_at）+ 被多个模块共享 → 独立文件

### Q2：数据表是什么时候被创建的？

两套机制，分工明确：

**生产/开发** → Alembic 迁移，手动执行 `alembic upgrade head`
- 读取 `alembic/versions/0347343374b3_initial_schema.py` 的 `upgrade()` 函数
- 支持版本追踪、回滚、增量变更
- `alembic/env.py` 负责把 `.env` 里的 `DATABASE_URL` 传给 Alembic

**测试环境** → `conftest.py` 直接调用 `Base.metadata.create_all(bind=test_engine)`
- `scope="session", autouse=True`：整个测试会话开始时执行一次
- 每个测试后只 TRUNCATE 清数据，不重建表（更快）

**关键细节**：`main.py` 里没有 `create_all()`，应用启动时不会自动建表，新环境必须先手跑 Alembic。

### Q3：TEST_DATABASE_URL 是什么？

`conftest.py` 里的二选一兜底逻辑：
```python
TEST_DATABASE_URL = settings.test_database_url or settings.database_url.replace(
    "/test_center", "/test_center_test"
)
```
- 优先读 `.env` 里的 `TEST_DATABASE_URL`（`config.py` 默认值为 `""`）
- 为空则自动把主库 URL 的库名 `test_center` 替换为 `test_center_test`

结果：测试库与主库同实例不同库名，测试数据不污染主库。特殊情况（测试库在另一台服务器）才需要手动配。

### Q4：哪里会先读 .env 里的配置？

`config.py` 中 `model_config = {"env_file": ".env"}` 告诉 pydantic-settings 自动读取 `.env`。
触发时机是最后一行 `settings = Settings()` 被执行时（模块首次被导入时）。
之后所有 `from app.core.config import settings` 拿到的都是已填充好的配置对象。

读取优先级：**环境变量 > .env 文件 > 字段默认值**，Docker/CI 里设环境变量会自动覆盖 .env。

### Q5：pydantic_settings BaseSettings 有什么用？

专门管理配置的 Pydantic 类，解决 `os.getenv()` 的缺陷：

| 能力 | 说明 |
|------|------|
| 自动读环境变量 | 字段名对应变量名，无需手动 `os.getenv()` |
| 类型自动转换 | 环境变量都是字符串，`int`/`bool` 字段自动转换 |
| 必填项启动校验 | 无默认值的字段若缺失，实例化时立即报 `ValidationError`，不等运行时崩 |
| 支持 `.env` 文件 | `model_config = {"env_file": ".env"}`，本地开发和生产代码不变 |
| 多环境优先级 | 环境变量 > .env > 默认值，天然支持覆盖 |

一句话：`BaseSettings` = `os.getenv()` + 类型校验 + 启动时必填检查 + `.env` 支持。

### Q6：pydantic_settings 来源于什么包，在当前项目还有什么作用？

来源：`pydantic-settings==2.2.1`（Pydantic v2 时从主包拆出，需独立安装）。

项目中 `pydantic_settings`（BaseSettings）**只用在 `config.py`**。

但 `pydantic`（BaseModel）遍布所有 `schemas.py`，负责 API 请求/响应数据校验：

| | pydantic | pydantic-settings |
|---|---|---|
| 核心类 | BaseModel | BaseSettings（继承 BaseModel）|
| 用途 | 校验 API 数据 | 读取环境变量/配置文件 |
| 用在 | 所有 schemas.py | 只有 config.py |

`BaseSettings` 本质是加了"从环境变量读值"能力的 `BaseModel`，校验逻辑完全共用。

### Q7：config.py 中的 settings 变量是否就是一个全局变量？

是，模块级全局变量，且是**模块单例**。
Python 模块导入有缓存，同一模块无论被 import 多少次只执行一次，`settings = Settings()` 只运行一次，整个进程只有一个实例。
`database.py`、`security.py`、`conftest.py` 拿到的是同一个对象，不会重复读 `.env`。
这是 Python 项目管理"只读、全局"配置的惯用写法。
