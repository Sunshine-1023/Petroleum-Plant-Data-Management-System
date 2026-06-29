from django.urls import path

from . import views

urlpatterns = [
    # 登录接口
    path('auth/login/', views.auth_login, name='auth-login'),
    path('system/status/', views.system_status, name='system-status'),

    # 第一阶段：查询接口
    path('health/', views.health_check, name='health-check'),
    path('stats/', views.stats_overview, name='stats-overview'),
    path('db-test/', views.db_test, name='db-test'),
    path('depts/', views.dept_list, name='dept-list'),
    path('depts/<str:dept_code>/overview/', views.dept_overview, name='dept-overview'),

    # 第二阶段：更新接口
    path('projects/<str:bill_no>/costs/', views.update_project_costs, name='update-project-costs'),
    path('material-details/', views.create_material_detail, name='create-material-detail'),
    path('material-details/<int:detail_id>/', views.update_material_detail, name='update-material-detail'),

    # 第三阶段：数据库技术点接口
    path('projects/create-with-materials/', views.create_project_with_materials, name='create-project-with-materials'),
    path('projects/<str:bill_no>/', views.project_detail, name='project-detail'),
    path('views/project-material/', views.view_project_material, name='view-project-material'),
    path('procedures/dept-cost/<str:dept_code>/', views.procedure_dept_cost, name='procedure-dept-cost'),
    path('cursor/dept-summary/', views.cursor_dept_summary, name='cursor-dept-summary'),
    path('cursors/dept-summary/', views.cursor_dept_summary, name='cursor-dept-summary-alias'),
]
