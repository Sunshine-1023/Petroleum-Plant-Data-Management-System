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

## 0、环境配置总览（必看）

本项目运行依赖由 **Python + Node + MySQL + 环境变量** 组成，建议先按本节核对，再执行安装步骤。

### 0.1 软件版本建议

| 组件 | 建议版本 | 用途 | 验证命令 |
|------|----------|------|----------|
| Python | 3.9+ | 后端 Django/DRF | `python --version` |
| pip | 21+ | 安装后端依赖 | `pip --version` |
| Node.js | 18+（推荐 20 LTS） | 前端构建/运行 | `node --version` |
| npm | 8+ | 安装前端依赖 | `npm --version` |
| MySQL | 8.x | 业务数据库 | `SELECT VERSION();` |
| Navicat | 任意可用版本 | 可视化管理数据库 | - |

### 0.2 端口与地址约定

| 服务 | 地址 | 说明 |
|------|------|------|
| 后端 Django | `http://127.0.0.1:8000` | API 服务 |
| 前端 Vite | `http://localhost:5173` | 页面访问入口 |
| MySQL | `127.0.0.1:3306` | 数据库连接 |

### 0.3 后端环境变量（`backend/.env`）

请以 `backend/.env.example` 为模板创建，完整含义如下：

```env
# Django
SECRET_KEY=change-me-to-a-random-secret-key   # Django 密钥，生产环境必须更换
DEBUG=True                                    # 开发环境 True，生产环境 False
ALLOWED_HOSTS=127.0.0.1,localhost             # 允许访问主机

# MySQL
DB_NAME=zyxt                                  # 数据库名（与 init_mysql.sql 保持一致）
DB_USER=root                                  # 数据库用户名（可改 CYGLXT）
DB_PASSWORD=your_mysql_password               # 数据库密码
DB_HOST=127.0.0.1                             # 数据库主机
DB_PORT=3306                                  # 数据库端口

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> 若老师要求验收账号：可将 `DB_USER/DB_PASSWORD` 改为 `CYGLXT/学号`。

### 0.4 前端环境变量（`frontend/.env`）

```env
VITE_API_BASE_URL=/api
```

说明：前端默认通过 Vite 代理把 `/api` 请求转发到 `http://127.0.0.1:8000`。

### 0.5 关键配置文件说明

| 文件 | 作用 |
|------|------|
| `backend/config/settings.py` | Django 全局配置（数据库、CORS、APP） |
| `backend/.env` | 本地后端环境变量（不提交） |
| `backend/.env.example` | 后端环境变量模板 |
| `frontend/.env` | 前端运行环境变量 |
| `frontend/vite.config.js` | 前端开发代理配置 |
| `scripts/init_mysql.sql` | 初始化创建 `zyxt` 数据库 |
| `scripts/sql/04_advanced_objects.sql` | 索引/存储过程/触发器/权限 |

### 0.6 启动前 1 分钟自检清单

- [ ] `backend/.env` 已填写正确数据库账号密码
- [ ] MySQL 服务已启动且可连接
- [ ] `zyxt` 库已创建，实验数据已导入
- [ ] 已执行 `scripts/sql/04_advanced_objects.sql`
- [ ] `python manage.py check` 无错误
- [ ] `npm run build` 可成功

---

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

## 一-B、Windows 安装与运行说明（PowerShell）

以下步骤适用于 Windows 10/11，建议使用 **PowerShell**。

### 1) 安装基础软件

请先安装并确认以下软件可用：

- Python 3.9+（勾选 *Add Python to PATH*）
- Node.js LTS（包含 npm）
- MySQL 8（或已可用的 MySQL 服务）
- Navicat（用于图形化管理数据库）

验证命令：

```powershell
python --version
pip --version
node --version
npm --version
```

### 2) 进入项目目录并准备虚拟环境

```powershell
cd "C:\你的路径\数据库实践"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r .\backend\requirements.txt
```

> 如果你项目里已经有 `.venv`，可直接执行 `.\.venv\Scripts\activate`。

### 3) 安装前端依赖

```powershell
cd .\frontend
npm install
cd ..
```

### 4) 初始化数据库

推荐在 Navicat 执行：

- `scripts/init_mysql.sql`
- 实验 1-6 的建表和数据 SQL
- `scripts/sql/04_advanced_objects.sql`

如使用命令行（已安装 mysql 客户端）：

```powershell
mysql -u root -p < .\scripts\init_mysql.sql
```

### 5) 配置后端数据库连接

编辑 `backend/.env`：

```env
DB_NAME=zyxt
DB_USER=你的数据库用户名
DB_PASSWORD=你的数据库密码
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 6) 启动项目（两个终端）

**终端 A（后端）：**

```powershell
cd "C:\你的路径\数据库实践\backend"
..\.venv\Scripts\activate
python manage.py runserver
```

> 如果 `..\.venv\Scripts\activate` 无法执行，请改用：
>
> ```powershell
> cd "C:\你的路径\数据库实践"
> .\.venv\Scripts\activate
> cd .\backend
> python manage.py runserver
> ```

**终端 B（前端）：**

```powershell
cd "C:\你的路径\数据库实践\frontend"
npm run dev
```

浏览器访问：`http://localhost:5173`

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
