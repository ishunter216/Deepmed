from django.urls import path

from base import views as base_views

urlpatterns = [
    path('reports/',
         base_views.ReportDataView.as_view(),
         name='reports'),
    path('chart/',
         base_views.ChartOneView.as_view(),
         name='chart'),
    path('test/',
         base_views.TestDataView.as_view(),
         name='tests'),
    path('resources/',
         base_views.ResourcesView.as_view(),
         name='resources'),
]
