from django.urls import path

from . import views

app_name = 'dox'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:topic_id>/', views.detail, name='detail'),
    path('app_dox', views.per_app_docs, name='per_app_dox'),
    path('app_dox_detail/<int:topic_id>/', views.sv_detail, name='app_dox_detail'),
]
