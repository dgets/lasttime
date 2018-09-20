from django.urls import path

from . import views

app_name = 'recadm'
urlpatterns = [
    path('<int:topic_id>/', views.detail, name='detail'),
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('save_admin', views.save_admin, name='save_admin'),
]

