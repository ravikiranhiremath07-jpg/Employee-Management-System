from django.urls import path
from payroll import views

urlpatterns = [
    path('', views.salary_list_view, name='salary_list'),
    path('add/', views.salary_add_view, name='salary_add'),
    path('<int:pk>/statement/', views.salary_detail_view, name='salary_detail'),
    path('<int:pk>/edit/', views.salary_edit_view, name='salary_edit'),
    path('my-statements/', views.my_salary_view, name='my_salary'),
]
