# Frontend Design Spec — Test Center

日期：2026-06-05

---

## 一、概述

为 test-center FastAPI 后端新增 React 前端，覆盖登录、应用列表、测试用例、缺陷管理四个核心模块。风格简约，以 Ant Design 为基础组件库。

**技术栈：**
- React 18 + Vite
- Ant Design 5
- React Router v6
- React Query v5
- axios

---

## 二、项目结构

前端代码放在项目根目录的 `frontend/` 下，与后端 `app/` 并列：

```
test-center/
├── app/                        ← FastAPI 后端（不改动）
├── frontend/
│   ├── index.html
│   ├── vite.config.ts          ← dev 模式 proxy /api → localhost:8000
│   ├── src/
│   │   ├── main.tsx
│   │   ├── router.tsx          ← 路由定义
│   │   ├── api/
│   │   │   ├── client.ts       ← axios 实例 + JWT 拦截器
│   │   │   ├── auth.ts
│   │   │   ├── apps.ts
│   │   │   ├── testCases.ts
│   │   │   └── defects.ts
│   │   ├── pages/
│   │   │   ├── Login/
│   │   │   ├── AppList/
│   │   │   ├── TestCases/
│   │   │   └── Defects/
│   │   ├── components/
│   │   │   └── AppLayout/      ← 顶栏 + 侧边栏框架
│   │   ├── hooks/              ← React Query hooks
│   │   └── context/
│   │       └── AuthContext.tsx ← 当前用户 + 角色信息
│   └── package.json
```

**生产部署：** `vite build` 输出 `frontend/dist/`，FastAPI 用 `StaticFiles` 挂载并托管，前后端同源，无需 CORS 配置。

---

## 三、路由设计

| 路径 | 页面 | 是否需要登录 |
|------|------|-------------|
| `/login` | 登录页 | 否 |
| `/apps` | 应用列表（首页） | 是 |
| `/apps/:appId/test-cases` | 测试用例列表 | 是 |
| `/apps/:appId/test-cases?caseId=:caseId` | 用例详情（右侧抽屉，URL 带 query param，不跳新页面） | 是 |
| `/apps/:appId/defects` | 缺陷列表 | 是 |
| `/apps/:appId/defects/:defectId` | 缺陷详情页 | 是 |

未登录访问受保护路由 → 重定向到 `/login`。

---

## 四、整体布局（AppLayout）

布局 C：顶栏 + 二级侧边栏，登录后所有页面共用（应用列表页为全屏，不含侧边栏）。

```
┌─────────────────────────────────────────────────────┐
│  ⚡ Test Center  │  当前应用: 电商平台 ▾  │  admin 退出 │  ← AppHeader (48px)
├──────────────┬──────────────────────────────────────┤
│  📋 测试用例  │  面包屑导航                           │
│  ✅ 测试任务  │  页面标题 + 操作按钮                   │
│  🐛 缺陷管理  │                                      │  ← AppSider (140px)
│              │  内容主体 <Outlet />                   │
│  🏠 应用列表  │                                      │
└──────────────┴──────────────────────────────────────┘
```

- **AppHeader**：Logo、应用切换下拉（Select，调 `GET /api/v1/apps` 填充选项）、用户名、退出按钮
- **AppSider**：当前 appId 下的模块导航，高亮当前路由。测试任务链接本次暂不实现，显示为 disabled 状态
- **内容区**：React Router `<Outlet />`，面包屑 + 标题行 + 主体

---

## 五、各页面设计

### 5.1 登录页（`/login`）

居中卡片，白底灰背景。字段：用户名、密码。提交调 `POST /api/v1/auth/login`，成功后 token 存 `localStorage`，跳转 `/apps`。

### 5.2 应用列表（`/apps`）

全屏页，无侧边栏。顶部搜索栏（前端实时过滤，不发额外请求）+ 卡片网格（3 列）。每张卡片展示：应用名、code、描述、版本数、"进入"链接。admin 角色显示"新建应用"按钮。

### 5.3 测试用例列表（`/apps/:appId/test-cases`）

表格展示，列：用例名称、优先级、分类、是否自动化、操作。顶部过滤栏：搜索名称、优先级下拉、分类下拉。点"查看"弹出**右侧抽屉**展示详情（前置条件、测试步骤、预期结果），同时将 `?caseId=xxx` 写入 URL，支持刷新保留抽屉状态。admin / tester 角色显示"新建用例"按钮和删除操作。

### 5.4 缺陷列表（`/apps/:appId/defects`）

表格展示，列：缺陷编号、标题、严重度、状态、指派给、操作。顶部过滤栏：状态下拉、严重度下拉。点缺陷编号或"查看"跳转缺陷详情页。admin / tester 角色显示"提缺陷"按钮。

### 5.5 缺陷详情（`/apps/:appId/defects/:defectId`）

独立页面（内容较多，适合整页展示）。分为三块：
1. **基本信息**：标题、状态 Badge、严重度、优先级、指派给、版本、描述、复现步骤、预期/实际结果
2. **状态流转**：根据当前状态和当前用户角色，动态展示可操作的流转按钮（对应后端状态机），点击弹 Modal 确认 + 可填写备注
3. **评论区**：历史评论列表 + 发表评论输入框

---

## 六、Auth + API 层

### JWT 处理

- 登录后 token 存 `localStorage('token')`
- `api/client.ts` axios 实例的请求拦截器自动附加 `Authorization: Bearer <token>`
- 响应拦截器：401 → 清除 token → `window.location.href = '/login'`

### 当前用户信息

- 登录后调 `GET /api/v1/auth/me`，结果存入 `AuthContext`
- 全局可读 `currentUser.roles`，用于控制 UI 操作权限

### 角色-操作映射

| 操作 | 可见角色 |
|------|---------|
| 新建应用 | admin |
| 新建测试用例 / 测试任务 | admin, tester |
| 删除测试用例 | admin, tester |
| 提缺陷 | admin, tester |
| 状态流转按钮 | 按后端状态机规则动态展示 |
| 只读用户 | 仅查看，无操作按钮 |

### 应用可见性

所有登录用户看到全量应用列表（后端无过滤）。per-user 应用权限为未来功能，当前不实现。

### React Query hooks

每个资源一个 hook，统一处理 loading / error / 缓存：
- `useApps()` → `GET /api/v1/apps`
- `useTestCases(appId)` → `GET /api/v1/apps/:appId/test-cases`
- `useDefects(appId)` → `GET /api/v1/apps/:appId/defects`
- `useDefect(defectId)` → `GET /api/v1/defects/:defectId`

---

## 七、不在本次范围内

- 测试任务（`/test-tasks`）页面：列表和执行记录，后续迭代
- 用户管理 / 角色分配页面
- per-user 应用权限
- 移动端适配
