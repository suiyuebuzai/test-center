# 测试设计说明

> 记录 test-center 项目的测试策略、结构设计与关键决策。
> 最后更新：2026-06-05

---

## 一、两层测试结构

测试按性质分为两类，互不混淆：

| 层级 | 文件 | 类型 | 依赖 |
|------|------|------|------|
| 纯单元测试 | `test_state_machine.py` | 函数级 | 无 DB、无 HTTP |
| 集成测试 | `test_auth.py` 等 | API 级 | 真实 DB + HTTP |

### 纯单元测试 — `test_state_machine.py`

`state_machine.py` 只包含两个字典和一个纯函数 `validate_transition()`，无任何外部依赖，直接调用即可测试，不需要任何 fixture。

覆盖三类场景：

```
合法流转（8 个）     → 不抛异常即通过
非法状态跳转（4 个） → 抛 BusinessError(code="INVALID_TRANSITION")
权限不足（3 个）     → 抛 BusinessError(code="TRANSITION_FORBIDDEN")
多角色兼容（1 个）   → 任意一个角色满足条件即通过
```

### 集成测试

走完整链路：HTTP 请求 → FastAPI 路由 → Service → 真实数据库。验证业务逻辑在真实环境下的行为，覆盖 happy path 和错误路径。

---

## 二、conftest.py 三个关键决策

### 决策 1：真实数据库，不 Mock

```python
test_engine = create_engine(TEST_DATABASE_URL)  # 连真实 PostgreSQL 测试库
```

`get_db` 通过 `dependency_overrides` 替换为指向测试库的 session，而非 Mock 对象。

**原因**：Mock DB 会掩盖真实的 SQL 约束、CASCADE 删除、序列自增等行为。
例如 `test_defect_no_auto_increment` 依赖数据库实际执行的序列逻辑，Mock 无法验证。

### 决策 2：Session 级建表 + Function 级清数据

```python
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)  # 整个会话只建一次表
    # 预置角色数据
    ...

@pytest.fixture(autouse=True)
def clean_tables():
    yield
    # 每个 test 结束后 TRUNCATE 所有业务表
    conn.execute(text("TRUNCATE TABLE defects RESTART IDENTITY CASCADE"))
    ...
```

- `RESTART IDENTITY`：重置序列，避免 ID 累积影响断言
- `CASCADE`：自动处理外键约束，无需手动按依赖顺序删除
- 每个测试结束即清理，互不干扰，可任意顺序运行

### 决策 3：预置角色，不预置用户

角色（admin / tester / developer / readonly）是静态配置数据，在 `setup_test_db` 中写入，不在 `clean_tables` 中清除。

每个测试用例自己注册所需用户，保持测试的独立性和可读性。

---

## 三、集成测试的 Fixture 模式

以 `test_defects.py` 为例，用局部 `setup` fixture 封装前置状态：

```python
@pytest.fixture
async def setup(client):
    # 注册 admin → 建应用 → 建版本 → 注册 developer
    return admin_token, dev_token, app_id, version_id
```

每个测试只关注**被测行为本身**，前置条件由 fixture 负责，测试代码保持简洁。

```python
async def test_create_defect(client, setup):
    admin_token, _, app_id, version_id = setup
    resp = await client.post(...)   # 直接测重点
    assert resp.status_code == 201
```

---

## 四、覆盖策略

| 测试文件 | 类型 | 覆盖重点 |
|----------|------|---------|
| `test_state_machine.py` | 纯单元 | 状态机逻辑：合法/非法流转、角色权限 |
| `test_auth.py` | 集成 | 注册、登录、Token 验证、鉴权失败 |
| `test_defects.py` | 集成 | 缺陷创建、编号自增、状态流转、评论、历史记录 |
| `test_applications.py` | 集成 | 应用/版本 CRUD |
| `test_test_cases.py` | 集成 | 测试用例 CRUD |
| `test_test_tasks.py` | 集成 | 测试任务、执行记录 |

**总计：39 个测试用例，全部通过（Phase 1，2026-06-05）**

---

## 五、核心原则

1. **纯逻辑单独测**：无依赖的函数直接调用，快速、精准定位问题
2. **有 IO 就走全链路**：HTTP + 真实 DB，避免 Mock 掩盖真实问题
3. **每个测试独立**：`clean_tables` autouse 确保状态隔离，可任意顺序运行
4. **前置条件封装进 fixture**：测试代码只描述行为，不重复写样板代码
