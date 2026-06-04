from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('submit/<uuid:submission_id>/', views.submit_feedback, name='submit_feedback'),
    path('report/<uuid:submission_id>/', views.report_content, name='report_content'),
]
