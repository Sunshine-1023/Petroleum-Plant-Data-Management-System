# 后端 API 接口文档

## 启动

```bash
cd backend
source ../.venv/bin/activate
python manage.py runserver
```

## 第一阶段：查询接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/db-test/` | GET | 数据库连接测试 |
| `/api/depts/` | GET | 查询所有单位 |
| `/api/depts/<DeptCode>/overview/` | GET | 按单位代码查询总览 |

## 第二阶段：更新接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/projects/<BillNo>/costs/` | PUT | 更新作业项目成本 |

**请求体示例：**

```json
{
  "MaterialCost": 7100,
  "LaborCost": 2500,
  "EquipmentCost": 1000,
  "OtherCost": 1400,
  "SettlementAmount": 12000,
  "AccountAmount": 12000
}
```

**注意：** 数据库存在触发器 `trg_project_update_time_restrict`，仅允许**周一至周五 08:00–18:00** 更新 project 表。周末或夜间测试会返回错误，请在工作时间测试或于 Navicat 中临时禁用该触发器。

**报告截图建议：** 返回 JSON 中的 `before` 和 `after` 字段 + Navicat 中对应记录对比。

## 第三阶段：数据库技术点接口

| 接口 | 方法 | 技术点 | 代码位置 |
|------|------|--------|----------|
| `/api/views/project-material/` | GET | 视图 | `api/views.py` → `view_project_material` |
| `/api/procedures/dept-cost/<DeptCode>/` | GET | 存储过程 | `api/views.py` → `procedure_dept_cost` |
| `/api/cursor/dept-summary/` | GET | 游标 | `api/views.py` → `cursor_dept_summary` |
| `/api/projects/create-with-materials/` | POST | 事务 | `api/views.py` → `create_project_with_materials` |

**事务接口请求体示例：**

```json
{
  "project": {
    "BillNo": "zy2018099",
    "BudgetDept": "112201001",
    "WellNo": "y001",
    "BudgetAmount": 5000,
    "BudgetPerson": "张三",
    "BudgetDate": "2018-06-01",
    "StartDate": "2018-06-02",
    "EndDate": "2018-06-10",
    "CompanyName": "作业公司作业一队",
    "WorkContent": "测试作业",
    "LaborCost": 1000,
    "EquipmentCost": 500,
    "OtherCost": 200
  },
  "materials": [
    {"MaterialCode": "wm001", "Quantity": 10, "Price": 50},
    {"MaterialCode": "wm002", "Quantity": 5, "Price": 100}
  ]
}
```

## 数据库对象安装

在 Navicat 中对 `zyxt` 数据库执行：

```
scripts/sql/04_advanced_objects.sql
```

包含：存储过程、触发器、索引、CYGLXT 用户权限。

## 技术要点对照

| 技术 | SQL/代码文件 | 说明 |
|------|-------------|------|
| 索引 | `04_advanced_objects.sql` | BudgetDept、WellNo、DeptCode 等 |
| 视图 | 已有 `v_project_material` 等 | 后端直接 SELECT 视图 |
| 存储过程 | `sp_dept_cost_summary` | 单位成本统计 |
| 游标 | `sp_dept_summary_cursor` | 遍历 dept 逐部门统计 |
| 触发器 | `trg_material_detail_calc_amount` | 自动计算 Amount |
| 触发器 | `trg_material_detail_update_project_cost` | 自动更新 MaterialCost |
| 事务 | `create_project_with_materials` | Django `transaction.atomic()` |
| 用户权限 | `CREATE USER 'CYGLXT'` | 见 SQL 脚本 |
