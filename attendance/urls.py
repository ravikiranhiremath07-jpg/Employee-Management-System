from django.urls import path
from attendance import views

urlpatterns = [
    path('', views.attendance_list_view, name='attendance_list'),
    path('mark/', views.attendance_mark_view, name='attendance_mark'),
    path('<int:pk>/edit/', views.attendance_edit_view, name='attendance_edit'),
    path('my-history/', views.my_attendance_view, name='my_attendance'),
]
