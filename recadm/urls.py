from django.urls import path

from . import views

app_name = 'recadm'
urlpatterns = [
    path('<int:topic_id>/', views.detail, name='detail'),
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('save_admin', views.save_admin, name='save_admin'),
    path('edit/<int:admin_id>/', views.edit, name='edit'),
    path('add_usual_suspect', views.add_usual_suspect, name='add_usual_suspect'),
    path('save_usual_suspect_admin', views.save_usual_suspect_admin, name='save_usual_suspect_admin'),
]

