from django.urls import path
from . import views, api_views

urlpatterns = [
    # HTML pages
    path('', views.index, name='index'),
    path('analyze/', views.analyze_view, name='analyze'),
    path('result/<uuid:analysis_id>/', views.result_view, name='result'),
    path('history/', views.history_view, name='history'),

    # REST API
    path('api/analyze/', api_views.api_analyze, name='api_analyze'),
    path('api/result/<uuid:analysis_id>/', api_views.api_result, name='api_result'),
    path('api/history/', api_views.api_history, name='api_history'),
    path('api/ablation/<uuid:analysis_id>/', api_views.api_ablation, name='api_ablation'),
    path('api/delete/<uuid:analysis_id>/', api_views.api_delete, name='api_delete'),
    path('api/health/', api_views.api_health, name='api_health'),
]
