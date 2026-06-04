from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('moderation/', views.content_moderation, name='content_moderation'),
    path('models/', views.model_management, name='model_management'),
    path('analytics/', views.system_analytics, name='system_analytics'),
]
