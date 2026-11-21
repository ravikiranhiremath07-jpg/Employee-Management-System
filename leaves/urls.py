from django.urls import path
from leaves import views

urlpatterns = [
    path('', views.leave_list_view, name='leave_list'),
    path('apply/', views.leave_apply_view, name='leave_apply'),
    path('<int:pk>/review/', views.leave_review_view, name='leave_review'),
    path('my-history/', views.my_leaves_view, name='my_leaves'),
]
