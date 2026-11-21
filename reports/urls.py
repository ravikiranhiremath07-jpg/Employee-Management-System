from django.urls import path
from reports import views

urlpatterns = [
    path('', views.reports_dashboard_view, name='reports'),
    path('export/employees/', views.export_employees_csv, name='export_employees_csv'),
    path('export/attendance/', views.export_attendance_csv, name='export_attendance_csv'),
    path('export/leaves/', views.export_leaves_csv, name='export_leaves_csv'),
    path('export/salaries/', views.export_salaries_csv, name='export_salaries_csv'),
    path('export/departments/', views.export_departments_csv, name='export_departments_csv'),
]
