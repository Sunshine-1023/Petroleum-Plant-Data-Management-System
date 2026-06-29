from django.db import connection


def fetch_all(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one(sql, params=None):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        return cursor.rowcount


def call_procedure(proc_name, params=None):
    params = params or []
    placeholders = ', '.join(['%s'] * len(params))
    sql = f'CALL {proc_name}({placeholders})' if params else f'CALL {proc_name}()'

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()] if columns else []

        while cursor.nextset():
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                extra = [dict(zip(columns, row)) for row in cursor.fetchall()]
                if extra:
                    rows = extra

        return rows
