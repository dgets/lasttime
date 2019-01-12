from django.urls import path

from . import views

app_name = "home"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create_user/', views.create_user_interface, name='create_user_interface'),
]
