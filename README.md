# 采油厂油水井作业成本管理系统

前后端分离的数据库实践大作业项目：Vue 3 + Django REST Framework + MySQL 8。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + JavaScript + Element Plus + Vue Router |
| 后端 | Python Django + Django REST Framework + PyMySQL |
| 数据库 | MySQL 8（库名 `zyxt`） |
| 管理工具 | Navicat |
| 架构 | B/S 前后端分离 |

## 项目结构

```
数据库实践/
├── backend/                 # Django + DRF 后端
│   ├── api/                 # 业务接口
│   ├── config/              # 项目配置
│   ├── API.md               # 接口详细文档
│   └── .env                 # 数据库连接配置（勿提交）
├── frontend/                # Vue 3 前端
│   └── src/views/           # 5 个业务页面
├── scripts/
│   ├── init_mysql.sql       # 创建 zyxt 数据库
│   ├── sql/04_advanced_objects.sql  # 索引/存储过程/触发器/用户（可重复执行）
│   ├── setup.sh             # 安装依赖
│   └── start-dev.sh         # 一键启动前后端
└── README.md
```

## 一、环境准备（Mac）

### Python

```bash
cd "/Users/sunshine/Desktop/数据库实践"
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Node.js

```bash
node --version
npm --version
```

未安装时从 https://nodejs.org/ 下载 LTS，或 `brew install node`。

### MySQL 8

确保 MySQL 服务已启动，默认端口 `3306`。

---

## 二、数据库初始化（按顺序执行）

### 步骤 1：创建数据库

在 Navicat 或命令行执行：

```bash
mysql -u root -p < scripts/init_mysql.sql
```

将创建数据库 **`zyxt`**（与后端 `DB_NAME` 一致）。

### 步骤 2：导入实验表与数据

导入实验 1-6 已完成的表结构与测试数据到 `zyxt`，核心表包括：

- `dept`、`well`、`project`、`material`、`material_detail`、`construct_unit`
- 视图：`v_budget_status`、`v_mine1_projects`、`v_project_material`

### 步骤 3：安装高级数据库对象（可重复执行）

在 Navicat 中对 `zyxt` 执行：

```
scripts/sql/04_advanced_objects.sql
```

脚本为**幂等设计**：索引、存储过程、触发器会先 `DROP IF EXISTS` 再创建；用户权限使用 `CREATE USER IF NOT EXISTS`。

包含内容：

| 类型 | 对象 |
|------|------|
| 索引 | `idx_project_budget_dept` 等 |
| 存储过程 | `sp_dept_cost_summary`、`sp_dept_summary_cursor` |
| 触发器 | 材料明细 Amount 自动计算、MaterialCost 自动汇总 |
| 用户 | `CYGLXT@localhost`（密码见脚本，可按学号修改） |

### 步骤 4：配置后端连接

编辑 `backend/.env`：

```env
DB_NAME=zyxt
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_HOST=127.0.0.1
DB_PORT=3306
```

> 若老师要求使用 `CYGLXT` 账号验收，将 `DB_USER` / `DB_PASSWORD` 改为对应值即可。

---

## 三、启动项目

**终端 1 — 后端**

```bash
cd backend
source ../.venv/bin/activate
python manage.py runserver
```

**终端 2 — 前端**

```bash
cd frontend
npm run dev
```

浏览器访问：http://localhost:5173

或使用一键脚本：

```bash
./scripts/start-dev.sh
```

---

## 四、前端页面

| 路由 | 页面 | 功能 |
|------|------|------|
| `/` | 首页 | 统计概览、数据库连接状态 |
| `/dept-query` | 单位查询 | 按单位代码查询油水井、项目、成本汇总 |
| `/cost-update` | 成本更新 | 修改作业项目成本 |
| `/view-query` | 视图查询 | 查询 `v_project_material` |
| `/db-demo` | 数据库技术演示 | 存储过程、事务、触发器、游标 |

---

## 五、后端 API 一览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health/` | GET | 健康检查 |
| `/api/stats/` | GET | 首页统计数据 |
| `/api/db-test/` | GET | 数据库连接测试 |
| `/api/depts/` | GET | 查询所有单位 |
| `/api/depts/<DeptCode>/overview/` | GET | 按单位代码查询总览 |
| `/api/projects/<BillNo>/costs/` | PUT | 更新作业项目成本 |
| `/api/views/project-material/` | GET | 查询视图 |
| `/api/procedures/dept-cost/<DeptCode>/` | GET | 调用存储过程 |
| `/api/cursor/dept-summary/` | GET | 游标统计 |
| `/api/projects/create-with-materials/` | POST | 事务新增项目+材料 |

详细说明见 [backend/API.md](backend/API.md)。

---

## 六、技术要点与代码位置

| 技术点 | 位置 |
|--------|------|
| 索引 | `scripts/sql/04_advanced_objects.sql` |
| 视图查询 | `backend/api/views.py` → `view_project_material` |
| 存储过程 | `scripts/sql/04_advanced_objects.sql` + `backend/api/views.py` → `procedure_dept_cost` |
| 游标 | `scripts/sql/04_advanced_objects.sql` + `backend/api/views.py` → `cursor_dept_summary` |
| 触发器 | `scripts/sql/04_advanced_objects.sql` |
| 事务 | `backend/api/views.py` → `create_project_with_materials` |
| 用户权限 | `scripts/sql/04_advanced_objects.sql` 末尾 `CYGLXT` |
| 单位代码查询 | `backend/api/views.py` → `dept_overview` |
| 成本更新 | `backend/api/views.py` → `update_project_costs` |

---

## 七、Navicat 连接参考

| 字段 | 值 |
|------|-----|
| 主机 | 127.0.0.1 |
| 端口 | 3306 |
| 数据库 | zyxt |
| 用户名 | root（或 CYGLXT） |

---

## 常见问题

**Q: 成本更新接口返回“只能在工作时间更新”**

数据库存在触发器 `trg_project_update_time_restrict`，仅允许周一至周五 08:00–18:00 更新 `project` 表。答辩演示时请在工作时间测试，或在 Navicat 中临时禁用该触发器。

**Q: 触发器演示时 MaterialCost 未自动更新**

请确认已执行 `scripts/sql/04_advanced_objects.sql` 中第 6 节触发器（`trg_material_detail_update_project_cost*`）。

**Q: 重复执行 SQL 脚本报错**

`04_advanced_objects.sql` 已改为幂等，可安全重复执行。若仍报错，检查是否在正确数据库 `zyxt` 下执行。

**Q: 前端无法连接后端**

确认 Django 在 8000 端口运行，Vite 在 5173 端口运行；前端通过代理将 `/api` 转发到后端。
# Petroleum-Plant-Data-Management-System
