#!/usr/bin/env python3
"""
用于第 13 章截图的后端功能检查脚本。

特点：
1) 终端输出按“截图位置 42~49”分段，便于直接截图。
2) 每个功能都打印 PASS/FAIL 与关键返回数据。
3) 不会在第一处失败就退出，方便一次看到全量结果。
"""

import json
import sys
import time
from urllib import error, request


class CheckError(Exception):
    pass


def now_id(prefix: str) -> str:
    return f"{prefix}{int(time.time() * 1000) % 100000000}"


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

    ok = status_code in expected_status
    return ok, status_code, parsed


def print_title(title):
    print("\n" + "=" * 84)
    print(title)
    print("=" * 84)


def print_json(label, payload):
    print(f"{label}:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    print_title(f"功能 13 后端接口检查（截图模式）- 服务地址: {base_url}")

    passed = 0
    failed = 0

    # 0) 健康检查
    ok, status_code, data = http_call(base_url, "GET", "/api/health/")
    if ok and data.get("status") == "ok":
        print("✅ 后端服务健康检查: PASS")
        passed += 1
    else:
        print(f"❌ 后端服务健康检查: FAIL (status={status_code})")
        print_json("返回", data)
        failed += 1
        print("\n后端不可用，后续检查无法继续。")
        sys.exit(1)

    # 获取样例参数
    ok, status_code, view_seed = http_call(base_url, "GET", "/api/views/project-material/")
    if not ok or not isinstance(view_seed.get("data"), list) or not view_seed["data"]:
        print("❌ 无法从视图获取样例数据，后续检查终止。")
        print_json("返回", view_seed)
        sys.exit(1)

    sample = view_seed["data"][0]
    dept_code = sample.get("BudgetDept")
    well_no = sample.get("WellNo")
    company_name = sample.get("CompanyName") or "作业公司作业一队"
    material_code = sample.get("MaterialCode")

    if not dept_code or not well_no or not material_code:
        print("❌ 样例字段不足，后续检查终止。")
        print_json("样例", sample)
        sys.exit(1)

    # 13.1 视图查询接口
    print_title("【截图位置 42】13.1 视图查询接口返回结果")
    ok, status_code, view_data = http_call(base_url, "GET", "/api/views/project-material/")
    if ok and isinstance(view_data.get("data"), list):
        print(f"✅ GET /api/views/project-material/ : PASS (status={status_code})")
        print(f"数据条数: {len(view_data.get('data', []))}")
        preview = {
            "message": view_data.get("message"),
            "view": view_data.get("view"),
            "first_row": view_data.get("data", [None])[0],
        }
        print_json("关键返回", preview)
        passed += 1
    else:
        print(f"❌ GET /api/views/project-material/ : FAIL (status={status_code})")
        print_json("返回", view_data)
        failed += 1

    # 13.2 存储过程调用接口
    print_title("【截图位置 44】13.2 存储过程调用接口返回结果")
    ok, status_code, proc_data = http_call(base_url, "GET", f"/api/procedures/dept-cost/{dept_code}/")
    if ok and isinstance(proc_data.get("data"), list):
        print(f"✅ GET /api/procedures/dept-cost/{dept_code}/ : PASS (status={status_code})")
        preview = {
            "message": proc_data.get("message"),
            "procedure": proc_data.get("procedure"),
            "first_row": proc_data.get("data", [None])[0],
        }
        print_json("关键返回", preview)
        passed += 1
    else:
        print(f"❌ GET /api/procedures/dept-cost/{dept_code}/ : FAIL (status={status_code})")
        print_json("返回", proc_data)
        failed += 1

    # 13.3 事务接口（提交成功）
    bill_ok = now_id("zyok")
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
        "materials": [{"MaterialCode": material_code, "Quantity": 3, "Price": 10}],
    }

    print_title("【截图位置 46】13.3 事务提交成功返回结果")
    ok, status_code, tx_ok_data = http_call(
        base_url,
        "POST",
        "/api/projects/create-with-materials/",
        payload=tx_ok_payload,
        expected_status=(201,),
    )
    if ok and "事务提交成功" in str(tx_ok_data.get("message", "")):
        print(f"✅ POST /api/projects/create-with-materials/ : PASS (status={status_code})")
        print_json("关键返回", tx_ok_data)
        passed += 1
    else:
        print(f"❌ POST /api/projects/create-with-materials/ : FAIL (status={status_code})")
        print_json("返回", tx_ok_data)
        failed += 1

    # 13.3 事务接口（回滚验证）
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
        # 用负数触发校验失败，期望事务回滚
        "materials": [{"MaterialCode": material_code, "Quantity": -1, "Price": 10}],
    }

    print_title("【截图位置 47】13.3 事务回滚验证返回结果")
    ok, status_code, tx_fail_data = http_call(
        base_url,
        "POST",
        "/api/projects/create-with-materials/",
        payload=tx_fail_payload,
        expected_status=(500,),
    )
    _, check_status, check_data = http_call(
        base_url,
        "GET",
        f"/api/projects/{bill_fail}/",
        expected_status=(404,),
    )
    rollback_ok = ok and ("事务回滚" in str(tx_fail_data.get("message", ""))) and check_status == 404
    if rollback_ok:
        print("✅ 事务回滚验证: PASS")
        print_json("回滚接口返回", tx_fail_data)
        print_json("回滚后单据查询（应404）", check_data)
        passed += 1
    else:
        print("❌ 事务回滚验证: FAIL")
        print_json("回滚接口返回", tx_fail_data)
        print_json("回滚后单据查询", check_data)
        failed += 1

    # 13.4 触发器验证接口（新增 + 更新）
    print_title("【截图位置 48】13.4 触发器验证前后对比")
    ok_post, post_status, trig_post = http_call(
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
    detail_id = trig_post.get("data", {}).get("detail", {}).get("DetailID")
    if detail_id is None:
        print(f"❌ 触发器新增验证: FAIL (status={post_status})")
        print_json("返回", trig_post)
        failed += 1
    else:
        ok_put, put_status, trig_put = http_call(
            base_url,
            "PUT",
            f"/api/material-details/{detail_id}/",
            payload={"Quantity": 5, "Price": 30},
            expected_status=(200,),
        )
        post_validation = trig_post.get("data", {}).get("trigger_validation", {})
        put_validation = trig_put.get("data", {}).get("trigger_validation", {})
        amount_ok = post_validation.get("amount_calculated") and put_validation.get("amount_calculated")
        sync_ok = post_validation.get("material_cost_synced") and put_validation.get("material_cost_synced")
        print(f"POST /api/material-details/ status={post_status}")
        print_json("新增触发器验证", post_validation)
        print(f"PUT /api/material-details/{detail_id}/ status={put_status}")
        print_json("更新触发器验证", put_validation)

        if ok_post and ok_put and amount_ok and sync_ok:
            print("✅ 触发器验证: PASS（Amount 自动计算 + MaterialCost 同步）")
            passed += 1
        elif ok_post and ok_put and amount_ok and not sync_ok:
            print("⚠️ 触发器接口可用，但 MaterialCost 同步触发器未生效")
            failed += 1
        else:
            print("❌ 触发器验证: FAIL")
            failed += 1

    # 13.5 游标调用接口
    print_title("【截图位置 49】13.5 游标接口返回结果")
    ok, status_code, cursor_data = http_call(base_url, "GET", "/api/cursors/dept-summary/")
    if ok and isinstance(cursor_data.get("data"), list):
        print(f"✅ GET /api/cursors/dept-summary/ : PASS (status={status_code})")
        preview = {
            "message": cursor_data.get("message"),
            "procedure": cursor_data.get("procedure"),
            "row_count": len(cursor_data.get("data", [])),
            "first_row": cursor_data.get("data", [None])[0],
        }
        print_json("关键返回", preview)
        passed += 1
    else:
        print(f"❌ GET /api/cursors/dept-summary/ : FAIL (status={status_code})")
        print_json("返回", cursor_data)
        failed += 1

    print_title("检查汇总")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    if failed == 0:
        print("🎉 所有功能检查通过，可直接用于截图。")
        sys.exit(0)
    print("⚠️ 存在失败项，请按输出信息修复后重跑。")
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 脚本执行异常: {e}")
        sys.exit(1)
