from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('submit/', views.submit_news, name='submit_news'),
    path('verify/', views.verify_news, name='verify_news'),
    path('result/<uuid:submission_id>/', views.verification_result, name='verification_result'),
    path('history/', views.news_history, name='news_history'),
    path('detail/<uuid:submission_id>/', views.submission_detail, name='submission_detail'),
]
