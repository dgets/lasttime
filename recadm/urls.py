from django.urls import path

from . import views

app_name = 'viewdox'
urlpatterns = [
    path('<int:topic_id>/', views.detail, name='detail'),
    path('add', views.add, name='add'),
    path('add_new', views.add_new, name='add_new'),
]

