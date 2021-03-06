from django.urls import path

from . import views

app_name = 'dataview'
urlpatterns = [
    # path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    path('<int:pk>/', views.SubAdminDataView.as_view(), name='data_summary'),
    path('constrained_summary/<int:sub_id>/', views.day_constrained_summary, name='constrained_summary'),
    path('halflife/<int:sub_id>/', views.extrapolate_halflife_data, name='halflife'),
    path('dump_dose_graph_data/<int:sub_id>/', views.dump_dose_graph_data, name='dump_dose_graph_data'),
    path('dump_interval_graph_data/<int:sub_id>/', views.dump_interval_graph_data, name='dump_interval_graph_data'),
    path('dump_constrained_dose_graph_data/<int:sub_id>/', views.dump_constrained_dose_graph_data,
         name='dump_constrained_dose_graph_data'),
    path('class_data_summary/<int:class_id>/', views.class_data_summary, name='class_data_summary'),
    path('sclasses/', views.sclasses, name='sclasses'),
]
