import pymysql
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .db_service import call_procedure, execute, fetch_all, fetch_one
from .db_utils import serialize_row, serialize_rows

PROJECT_COST_FIELDS = (
    'MaterialCost', 'LaborCost', 'EquipmentCost',
    'OtherCost', 'SettlementAmount', 'AccountAmount',
)

PROJECT_SELECT_SQL = '''
    SELECT
        BillNo, BudgetDept, WellNo, BudgetAmount,
        MaterialCost, LaborCost, EquipmentCost, OtherCost,
        SettlementAmount, AccountAmount
    FROM project
    WHERE BillNo = %s
'''


def _to_non_negative_number(value, field_name):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{field_name} 必须是数字')
    if number < 0:
        raise ValueError(f'{field_name} 不能为负数')
    return number


def _sync_project_material_cost(bill_no):
    """
    兜底同步 project.MaterialCost。
    当数据库缺少 material_detail -> project 同步触发器时，仍保证业务可用。
    """
    execute(
        '''
        UPDATE project
        SET MaterialCost = (
            SELECT COALESCE(SUM(Amount), 0)
            FROM material_detail
            WHERE BillNo = %s
        )
        WHERE BillNo = %s
        ''',
        [bill_no, bill_no],
    )


@api_view(['GET'])
def health_check(request):
    return Response({
        'status': 'ok',
        'message': 'Django REST API 運行正常',
    })


@api_view(['GET'])
def system_status(request):
    """用于前端展示后端与数据库运行状态。"""
    try:
        db_name = settings.DATABASES['default']['NAME']
        procedures = fetch_all(
            'SELECT ROUTINE_NAME FROM information_schema.routines WHERE routine_schema = %s AND routine_type = %s',
            [db_name, 'PROCEDURE'],
        )
        triggers = fetch_all(
            'SELECT TRIGGER_NAME FROM information_schema.triggers WHERE trigger_schema = %s',
            [db_name],
        )
        return Response({
            'message': '系统运行正常',
            'data': {
                'backend': 'ok',
                'database': db_name,
                'table_count': len(fetch_all('SHOW TABLES')),
                'procedure_count': len(procedures),
                'trigger_count': len(triggers),
            },
        })
    except Exception as exc:
        return Response(
            {'message': '系统状态检查失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def auth_login(request):
    """使用数据库用户名/密码进行登录校验。"""
    username = (request.data.get('username') or '').strip()
    password = request.data.get('password') or ''

    if not username or not password:
        return Response(
            {'message': '用户名和密码不能为空'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    db = settings.DATABASES['default']

    try:
        conn = pymysql.connect(
            host=db.get('HOST') or '127.0.0.1',
            port=int(db.get('PORT') or 3306),
            user=username,
            password=password,
            database=db.get('NAME'),
            charset='utf8mb4',
            connect_timeout=5,
        )
        with conn.cursor() as cursor:
            cursor.execute('SELECT DATABASE(), CURRENT_USER()')
            database_name, current_user = cursor.fetchone()
        conn.close()

        return Response({
            'message': '登录成功',
            'data': {
                'username': username,
                'database': database_name,
                'host': db.get('HOST') or '127.0.0.1',
                'port': int(db.get('PORT') or 3306),
                'current_user': current_user,
            },
        })
    except Exception:
        return Response(
            {'message': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(['GET'])
def project_detail(request, bill_no):
    """查询单个作业单详情，用于前端更新页预填。"""
    try:
        row = fetch_one(
            '''
            SELECT
                BillNo, BudgetDept, WellNo, BudgetAmount,
                MaterialCost, LaborCost, EquipmentCost, OtherCost,
                SettlementAmount, AccountAmount
            FROM project
            WHERE BillNo = %s
            ''',
            [bill_no],
        )
        if not row:
            return Response(
                {'message': f'未找到作业单号 {bill_no}'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'message': '查询成功', 'data': serialize_row(row)})
    except Exception as exc:
        return Response(
            {'message': '查询失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def stats_overview(request):
    try:
        return Response({
            'message': '查询成功',
            'data': {
                'dept_count': fetch_one('SELECT COUNT(*) AS count FROM dept')['count'],
                'well_count': fetch_one('SELECT COUNT(*) AS count FROM well')['count'],
                'project_count': fetch_one('SELECT COUNT(*) AS count FROM project')['count'],
                'material_count': fetch_one('SELECT COUNT(*) AS count FROM material')['count'],
            },
        })
    except Exception as exc:
        return Response(
            {'message': '查询失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def db_test(request):
    from django.conf import settings

    try:
        database_name = settings.DATABASES['default']['NAME']
        tables = fetch_all('SHOW TABLES')
        table_names = [list(row.values())[0] for row in tables]

        return Response({
            'message': 'MySQL 数据库连接成功',
            'database': database_name,
            'tables': table_names,
        })
    except Exception as exc:
        return Response(
            {'message': 'MySQL 数据库连接失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def dept_list(request):
    try:
        rows = fetch_all('SELECT DeptCode, DeptName FROM dept ORDER BY DeptCode')
        return Response({'message': '查询成功', 'data': serialize_rows(rows)})
    except Exception as exc:
        return Response(
            {'message': '查询失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def dept_overview(request, dept_code):
    try:
        dept = fetch_one(
            'SELECT DeptCode, DeptName FROM dept WHERE DeptCode = %s',
            [dept_code],
        )
        if not dept:
            return Response(
                {'message': f'未找到单位代码 {dept_code}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        wells = fetch_all(
            'SELECT WellNo, WellType, DeptCode FROM well WHERE DeptCode = %s ORDER BY WellNo',
            [dept_code],
        )
        projects = fetch_all(
            '''
            SELECT
                BillNo, BudgetDept, WellNo, BudgetAmount, BudgetPerson, BudgetDate,
                StartDate, EndDate, CompanyName, WorkContent,
                MaterialCost, LaborCost, EquipmentCost, OtherCost,
                SettlementAmount, SettlementPerson, SettlementDate,
                AccountAmount, AccountPerson, AccountDate
            FROM project
            WHERE BudgetDept = %s
            ORDER BY BillNo
            ''',
            [dept_code],
        )
        cost_summary = fetch_one(
            '''
            SELECT
                COUNT(*) AS project_count,
                COALESCE(SUM(BudgetAmount), 0) AS total_budget_amount,
                COALESCE(SUM(MaterialCost), 0) AS total_material_cost,
                COALESCE(SUM(LaborCost), 0) AS total_labor_cost,
                COALESCE(SUM(EquipmentCost), 0) AS total_equipment_cost,
                COALESCE(SUM(OtherCost), 0) AS total_other_cost,
                COALESCE(SUM(SettlementAmount), 0) AS total_settlement_amount,
                COALESCE(SUM(AccountAmount), 0) AS total_account_amount
            FROM project
            WHERE BudgetDept = %s
            ''',
            [dept_code],
        )

        return Response({
            'message': '查询成功',
            'data': {
                'dept': serialize_row(dept),
                'wells': serialize_rows(wells),
                'projects': serialize_rows(projects),
                'cost_summary': serialize_row(cost_summary),
            },
        })
    except Exception as exc:
        return Response(
            {'message': '查询失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['PUT'])
def update_project_costs(request, bill_no):
    """根据作业单号更新项目成本。返回修改前后数据，便于实验报告截图。"""
    try:
        before = fetch_one(PROJECT_SELECT_SQL, [bill_no])
        if not before:
            return Response(
                {'message': f'未找到作业单号 {bill_no}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = request.data
        missing = [field for field in PROJECT_COST_FIELDS if field not in payload]
        if missing:
            return Response(
                {'message': '缺少必填字段', 'missing_fields': missing},
                status=status.HTTP_400_BAD_REQUEST,
            )

        values = [_to_non_negative_number(payload[field], field) for field in PROJECT_COST_FIELDS] + [bill_no]
        execute(
            '''
            UPDATE project
            SET
                MaterialCost = %s,
                LaborCost = %s,
                EquipmentCost = %s,
                OtherCost = %s,
                SettlementAmount = %s,
                AccountAmount = %s
            WHERE BillNo = %s
            ''',
            values,
        )

        after = fetch_one(PROJECT_SELECT_SQL, [bill_no])
        return Response({
            'message': '更新成功',
            'data': {
                'before': serialize_row(before),
                'after': serialize_row(after),
            },
        })
    except Exception as exc:
        status_code = status.HTTP_400_BAD_REQUEST if isinstance(exc, ValueError) else status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(
            {'message': '更新失败', 'error': str(exc)},
            status=status_code,
        )


@api_view(['GET'])
def view_project_material(request):
    """查询视图 v_project_material。"""
    try:
        rows = fetch_all('SELECT * FROM v_project_material ORDER BY BillNo, DetailID')
        return Response({
            'message': '查询成功',
            'view': 'v_project_material',
            'data': serialize_rows(rows),
        })
    except Exception as exc:
        return Response(
            {'message': '查询失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def procedure_dept_cost(request, dept_code):
    """调用存储过程 sp_dept_cost_summary 统计单位作业成本。"""
    try:
        rows = call_procedure('sp_dept_cost_summary', [dept_code])
        if not rows:
            return Response(
                {'message': f'存储过程未返回数据，请确认 sp_dept_cost_summary 已创建'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'message': '查询成功',
            'procedure': 'sp_dept_cost_summary',
            'data': serialize_rows(rows),
        })
    except Exception as exc:
        return Response(
            {'message': '存储过程调用失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
def cursor_dept_summary(request):
    """调用游标存储过程 sp_dept_summary_cursor 统计各部门项目。"""
    try:
        rows = call_procedure('sp_dept_summary_cursor')
        return Response({
            'message': '查询成功',
            'procedure': 'sp_dept_summary_cursor',
            'data': serialize_rows(rows),
        })
    except Exception as exc:
        return Response(
            {'message': '游标存储过程调用失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def create_project_with_materials(request):
    """事务：新增作业项目 + 材料明细，失败则整体回滚。"""
    try:
        project = request.data.get('project')
        materials = request.data.get('materials', [])

        if not project or not project.get('BillNo'):
            return Response(
                {'message': '缺少 project 或 BillNo'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not materials:
            return Response(
                {'message': 'materials 不能为空'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bill_no = project['BillNo']
        existing = fetch_one('SELECT BillNo FROM project WHERE BillNo = %s', [bill_no])
        if existing:
            return Response(
                {'message': f'作业单号 {bill_no} 已存在'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            budget_amount = _to_non_negative_number(project.get('BudgetAmount', 0), 'BudgetAmount')
            material_cost = _to_non_negative_number(project.get('MaterialCost', 0), 'MaterialCost')
            labor_cost = _to_non_negative_number(project.get('LaborCost', 0), 'LaborCost')
            equipment_cost = _to_non_negative_number(project.get('EquipmentCost', 0), 'EquipmentCost')
            other_cost = _to_non_negative_number(project.get('OtherCost', 0), 'OtherCost')
            settlement_amount = _to_non_negative_number(project.get('SettlementAmount', 0), 'SettlementAmount')
            account_amount = _to_non_negative_number(project.get('AccountAmount', 0), 'AccountAmount')

            execute(
                '''
                INSERT INTO project (
                    BillNo, BudgetDept, WellNo, BudgetAmount, BudgetPerson, BudgetDate,
                    StartDate, EndDate, CompanyName, WorkContent,
                    MaterialCost, LaborCost, EquipmentCost, OtherCost,
                    SettlementAmount, SettlementPerson, SettlementDate,
                    AccountAmount, AccountPerson, AccountDate
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                ''',
                [
                    project.get('BillNo'),
                    project.get('BudgetDept'),
                    project.get('WellNo'),
                    budget_amount,
                    project.get('BudgetPerson'),
                    project.get('BudgetDate'),
                    project.get('StartDate'),
                    project.get('EndDate'),
                    project.get('CompanyName'),
                    project.get('WorkContent'),
                    material_cost,
                    labor_cost,
                    equipment_cost,
                    other_cost,
                    settlement_amount,
                    project.get('SettlementPerson'),
                    project.get('SettlementDate'),
                    account_amount,
                    project.get('AccountPerson'),
                    project.get('AccountDate'),
                ],
            )

            inserted_materials = []
            for item in materials:
                quantity = _to_non_negative_number(item['Quantity'], 'Quantity')
                price = _to_non_negative_number(item['Price'], 'Price')
                execute(
                    '''
                    INSERT INTO material_detail (BillNo, MaterialCode, Quantity, Price)
                    VALUES (%s, %s, %s, %s)
                    ''',
                    [
                        bill_no,
                        item['MaterialCode'],
                        quantity,
                        price,
                    ],
                )
                inserted_materials.append(item)

            # 兜底同步，避免缺少触发器时 project.MaterialCost 不更新
            _sync_project_material_cost(bill_no)

        project_row = fetch_one(PROJECT_SELECT_SQL, [bill_no])
        material_rows = fetch_all(
            'SELECT DetailID, BillNo, MaterialCode, Quantity, Price, Amount FROM material_detail WHERE BillNo = %s',
            [bill_no],
        )

        return Response({
            'message': '事务提交成功：作业项目及材料明细已全部写入',
            'data': {
                'project': serialize_row(project_row),
                'materials': serialize_rows(material_rows),
            },
        }, status=status.HTTP_201_CREATED)
    except Exception as exc:
        return Response(
            {
                'message': '事务回滚：写入失败，作业项目及材料明细均未保存',
                'error': str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def create_material_detail(request):
    """触发器验证：新增材料明细。"""
    try:
        payload = request.data
        required_fields = ['BillNo', 'MaterialCode', 'Quantity', 'Price']
        missing = [field for field in required_fields if field not in payload]
        if missing:
            return Response(
                {'message': '缺少必填字段', 'missing_fields': missing},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bill_no = payload['BillNo']
        material_code = payload['MaterialCode']
        quantity = _to_non_negative_number(payload['Quantity'], 'Quantity')
        price = _to_non_negative_number(payload['Price'], 'Price')

        project_before = fetch_one(
            'SELECT BillNo, MaterialCost, SettlementAmount FROM project WHERE BillNo = %s',
            [bill_no],
        )
        if not project_before:
            return Response(
                {'message': f'未找到作业单号 {bill_no}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        material_exists = fetch_one(
            'SELECT MaterialCode FROM material WHERE MaterialCode = %s',
            [material_code],
        )
        if not material_exists:
            return Response(
                {'message': f'未找到材料编码 {material_code}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        before_sum_row = fetch_one(
            'SELECT COALESCE(SUM(Amount), 0) AS total_amount FROM material_detail WHERE BillNo = %s',
            [bill_no],
        )
        before_sum = float(before_sum_row['total_amount'])

        with transaction.atomic():
            execute(
                '''
                INSERT INTO material_detail (BillNo, MaterialCode, Quantity, Price)
                VALUES (%s, %s, %s, %s)
                ''',
                [bill_no, material_code, quantity, price],
            )
            _sync_project_material_cost(bill_no)

        detail = fetch_one(
            '''
            SELECT DetailID, BillNo, MaterialCode, Quantity, Price, Amount
            FROM material_detail
            WHERE BillNo = %s AND MaterialCode = %s
            ORDER BY DetailID DESC
            LIMIT 1
            ''',
            [bill_no, material_code],
        )
        if not detail:
            return Response(
                {'message': '新增成功但未查询到明细记录'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        expected_amount = round(quantity * price, 2)
        actual_amount = float(detail['Amount']) if detail['Amount'] is not None else None

        after_sum_row = fetch_one(
            'SELECT COALESCE(SUM(Amount), 0) AS total_amount FROM material_detail WHERE BillNo = %s',
            [bill_no],
        )
        after_sum = float(after_sum_row['total_amount'])

        project_after = fetch_one(
            'SELECT BillNo, MaterialCost, SettlementAmount FROM project WHERE BillNo = %s',
            [bill_no],
        )
        material_cost_after = float(project_after['MaterialCost']) if project_after else None

        return Response(
            {
                'message': '材料明细新增成功',
                'data': {
                    'detail': serialize_row(detail),
                    'project_before': serialize_row(project_before),
                    'project_after': serialize_row(project_after),
                    'trigger_validation': {
                        'expected_amount': expected_amount,
                        'actual_amount': actual_amount,
                        'amount_calculated': actual_amount == expected_amount,
                        'before_material_sum': before_sum,
                        'after_material_sum': after_sum,
                        'material_cost_synced': material_cost_after == after_sum,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception as exc:
        return Response(
            {'message': '材料明细新增失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['PUT'])
def update_material_detail(request, detail_id):
    """触发器验证：更新材料明细。"""
    try:
        detail_before = fetch_one(
            '''
            SELECT DetailID, BillNo, MaterialCode, Quantity, Price, Amount
            FROM material_detail
            WHERE DetailID = %s
            ''',
            [detail_id],
        )
        if not detail_before:
            return Response(
                {'message': f'未找到明细ID {detail_id}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = request.data
        quantity = _to_non_negative_number(
            payload.get('Quantity', detail_before['Quantity']),
            'Quantity',
        )
        price = _to_non_negative_number(
            payload.get('Price', detail_before['Price']),
            'Price',
        )
        material_code = payload.get('MaterialCode', detail_before['MaterialCode'])
        bill_no = detail_before['BillNo']

        material_exists = fetch_one(
            'SELECT MaterialCode FROM material WHERE MaterialCode = %s',
            [material_code],
        )
        if not material_exists:
            return Response(
                {'message': f'未找到材料编码 {material_code}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        before_sum_row = fetch_one(
            'SELECT COALESCE(SUM(Amount), 0) AS total_amount FROM material_detail WHERE BillNo = %s',
            [bill_no],
        )
        before_sum = float(before_sum_row['total_amount'])
        project_before = fetch_one(
            'SELECT BillNo, MaterialCost, SettlementAmount FROM project WHERE BillNo = %s',
            [bill_no],
        )

        with transaction.atomic():
            execute(
                '''
                UPDATE material_detail
                SET MaterialCode = %s, Quantity = %s, Price = %s
                WHERE DetailID = %s
                ''',
                [material_code, quantity, price, detail_id],
            )
            _sync_project_material_cost(bill_no)

        detail_after = fetch_one(
            '''
            SELECT DetailID, BillNo, MaterialCode, Quantity, Price, Amount
            FROM material_detail
            WHERE DetailID = %s
            ''',
            [detail_id],
        )
        after_sum_row = fetch_one(
            'SELECT COALESCE(SUM(Amount), 0) AS total_amount FROM material_detail WHERE BillNo = %s',
            [bill_no],
        )
        after_sum = float(after_sum_row['total_amount'])
        project_after = fetch_one(
            'SELECT BillNo, MaterialCost, SettlementAmount FROM project WHERE BillNo = %s',
            [bill_no],
        )

        expected_amount = round(quantity * price, 2)
        actual_amount = float(detail_after['Amount']) if detail_after['Amount'] is not None else None
        material_cost_after = float(project_after['MaterialCost']) if project_after else None

        return Response(
            {
                'message': '材料明细更新成功',
                'data': {
                    'before': serialize_row(detail_before),
                    'after': serialize_row(detail_after),
                    'project_before': serialize_row(project_before),
                    'project_after': serialize_row(project_after),
                    'trigger_validation': {
                        'expected_amount': expected_amount,
                        'actual_amount': actual_amount,
                        'amount_calculated': actual_amount == expected_amount,
                        'before_material_sum': before_sum,
                        'after_material_sum': after_sum,
                        'material_cost_synced': material_cost_after == after_sum,
                    },
                },
            }
        )
    except Exception as exc:
        return Response(
            {'message': '材料明细更新失败', 'error': str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
