from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_roster, name='upload_roster'),
    path('export/', views.export_roster, name='export_roster'),
    path('update-shift/', views.update_shift, name='update_shift'),
    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('requests/', views.requests_view, name='requests'),
    path('manage-leave/<int:leave_id>/<str:action>/', views.manage_leave, name='manage_leave'),
    path('manage-swap/<int:swap_id>/<str:action>/', views.manage_swap, name='manage_swap'),
]
