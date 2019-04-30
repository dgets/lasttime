from django.urls import path

from . import views

app_name = "subadd"
urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add, name='add'),
    path('addentry', views.addentry, name='addentry'),
    path('<int:substance_id>/', views.detail, name='detail'),
    path('add_class', views.add_sub_class, name='add_sub_class'),
]

