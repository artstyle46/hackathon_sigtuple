from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('k-chart', views.chart, name='index'),
    path('c-chart', views.custom, name='index'),
    path('index', views.index, name='index'),
    path('report', views.report, name='report'),
    path('patient', views.search, name='patient'),
    re_path('report/(?P<report_id>[a-zA-Z0-9]+)$', views.show_report, name='show'),
]