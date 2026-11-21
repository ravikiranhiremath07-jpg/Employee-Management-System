from django.urls import path
from employees import views

urlpatterns = [
    path('', views.employee_list_view, name='employee_list'),
    path('add/', views.employee_add_view, name='employee_add'),
    path('<int:pk>/', views.employee_detail_view, name='employee_detail'),
    path('<int:pk>/edit/', views.employee_edit_view, name='employee_edit'),
    path('<int:pk>/delete/', views.employee_delete_view, name='employee_delete'),
    path('self-update/', views.employee_self_edit_view, name='employee_self_edit'),
]
