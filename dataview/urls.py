from django.urls import path

from . import views

app_name = 'dataview'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.SubAdminDataView.as_view(), name='data_summary')
]
