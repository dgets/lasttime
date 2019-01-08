from django.urls import path

from . import views

app_name = 'dataview'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.SubAdminDataView.as_view(), name='data_summary'),
    path('dump_graph_data/<int:sub_id>/', views.dump_graph_data, name='dump_graph_data'),
]
