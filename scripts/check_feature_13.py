#!/usr/bin/env python3
import json
import sys
import time
from urllib import error, request


def now_id(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 100000000}"


class CheckError(Exception):
    pass


def http_call(base_url, method, path, payload=None, expected_status=(200,)):
    url = f"{base_url.rstrip('/')}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(url=url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=12) as resp:
            status_code = resp.getcode()
            body = resp.read().decode("utf-8")
    except error.HTTPError as e:
        status_code = e.code
        body = e.read().decode("utf-8")
    except Exception as e:
        raise CheckError(f"{method} {path} 请求失败: {e}")

    try:
        parsed = json.loads(body) if body else {}
    except Exception:
        parsed = {"raw": body}

    if status_code not in expected_status:
        raise CheckError(
            f"{method} {path} 状态码 {status_code} 不在预期 {expected_status}，返回: {parsed}"
        )
    return status_code, parsed


def assert_true(condition, message):
    if not condition:
        raise CheckError(message)


def print_ok(msg):
    print(f"✅ {msg}")


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    print(f"开始检查功能 13，服务地址: {base_url}")

    # 0) 健康检查
    _, health = http_call(base_url, "GET", "/api/health/")
    assert_true(health.get("status") == "ok", "健康检查失败")
    print_ok("后端服务运行正常")

    # 1) 视图接口
    _, view_data = http_call(base_url, "GET", "/api/views/project-material/")
    rows = view_data.get("data", [])
    assert_true(isinstance(rows, list) and len(rows) > 0, "视图接口无数据")
    sample = rows[0]
    dept_code = sample.get("BudgetDept")
    well_no = sample.get("WellNo")
    company_name = sample.get("CompanyName") or "作业公司作业一队"
    material_code = sample.get("MaterialCode")
    assert_true(dept_code and well_no and material_code, "视图样例字段不足，无法继续检查")
    print_ok("13.1 视图接口正常")

    # 2) 存储过程接口
    _, proc_data = http_call(base_url, "GET", f"/api/procedures/dept-cost/{dept_code}/")
    proc_rows = proc_data.get("data", [])
    assert_true(isinstance(proc_rows, list) and len(proc_rows) > 0, "存储过程接口无返回数据")
    assert_true("project_count" in proc_rows[0], "存储过程返回缺少 project_count")
    print_ok("13.2 存储过程接口正常")

    # 3) 事务接口：成功提交
    bill_ok = now_id("zychk")
    tx_ok_payload = {
        "project": {
            "BillNo": bill_ok,
            "BudgetDept": dept_code,
            "WellNo": well_no,
            "BudgetAmount": 6000,
            "BudgetPerson": "检查脚本",
            "BudgetDate": "2024-01-01",
            "StartDate": "2024-01-02",
            "EndDate": "2024-01-10",
            "CompanyName": company_name,
            "WorkContent": "事务成功检查",
            "LaborCost": 500,
            "EquipmentCost": 300,
            "OtherCost": 100,
        },
        "materials": [
            {"MaterialCode": material_code, "Quantity": 3, "Price": 10},
        ],
    }
    _, tx_ok = http_call(
        base_url,
        "POST",
        "/api/projects/create-with-materials/",
        payload=tx_ok_payload,
        expected_status=(201,),
    )
    assert_true("事务提交成功" in tx_ok.get("message", ""), "事务成功接口返回异常")
    print_ok("13.3 事务接口（提交成功）正常")

    # 3-b) 事务接口：回滚验证（构造负数触发校验失败）
    bill_fail = now_id("zyfail")
    tx_fail_payload = {
        "project": {
            "BillNo": bill_fail,
            "BudgetDept": dept_code,
            "WellNo": well_no,
            "BudgetAmount": 6000,
            "BudgetPerson": "检查脚本",
            "BudgetDate": "2024-01-01",
            "StartDate": "2024-01-02",
            "EndDate": "2024-01-10",
            "CompanyName": company_name,
            "WorkContent": "事务回滚检查",
            "LaborCost": 500,
            "EquipmentCost": 300,
            "OtherCost": 100,
        },
        "materials": [
            {"MaterialCode": material_code, "Quantity": -1, "Price": 10},
        ],
    }
    _, tx_fail = http_call(
        base_url,
        "POST",
        "/api/projects/create-with-materials/",
        payload=tx_fail_payload,
        expected_status=(500,),
    )
    assert_true("事务回滚" in tx_fail.get("message", ""), "事务回滚接口返回异常")
    # 确认项目未写入
    http_call(
        base_url,
        "GET",
        f"/api/projects/{bill_fail}/",
        expected_status=(404,),
    )
    print_ok("13.3 事务接口（回滚验证）正常")

    # 4) 触发器验证接口：POST /api/material-details/
    _, trig_post = http_call(
        base_url,
        "POST",
        "/api/material-details/",
        payload={
            "BillNo": bill_ok,
            "MaterialCode": material_code,
            "Quantity": 2,
            "Price": 25,
        },
        expected_status=(201,),
    )
    trig_post_data = trig_post.get("data", {}).get("trigger_validation", {})
    assert_true(trig_post_data.get("amount_calculated") is True, "触发器新增校验失败：Amount 未自动计算")
    assert_true(trig_post_data.get("material_cost_synced") is True, "触发器新增校验失败：MaterialCost 未同步")
    detail_id = trig_post.get("data", {}).get("detail", {}).get("DetailID")
    assert_true(detail_id is not None, "触发器新增校验失败：未返回 DetailID")
    print_ok("13.4 触发器新增验证正常")

    # 4-b) 触发器验证接口：PUT /api/material-details/<DetailID>/
    _, trig_put = http_call(
        base_url,
        "PUT",
        f"/api/material-details/{detail_id}/",
        payload={
            "Quantity": 5,
            "Price": 30,
        },
        expected_status=(200,),
    )
    trig_put_data = trig_put.get("data", {}).get("trigger_validation", {})
    assert_true(trig_put_data.get("amount_calculated") is True, "触发器更新校验失败：Amount 未自动计算")
    assert_true(trig_put_data.get("material_cost_synced") is True, "触发器更新校验失败：MaterialCost 未同步")
    print_ok("13.4 触发器更新验证正常")

    # 5) 游标接口（按你文档路径）
    _, cursor_data = http_call(base_url, "GET", "/api/cursors/dept-summary/")
    cursor_rows = cursor_data.get("data", [])
    assert_true(isinstance(cursor_rows, list) and len(cursor_rows) > 0, "游标接口无返回数据")
    assert_true("DeptCode" in cursor_rows[0], "游标接口返回缺少 DeptCode")
    print_ok("13.5 游标接口正常")

    print("\n🎉 功能 13 全部检查通过：视图、存储过程、事务、触发器、游标接口可用。")


if __name__ == "__main__":
    try:
        main()
    except CheckError as e:
        print(f"\n❌ 检查失败：{e}")
        sys.exit(1)
