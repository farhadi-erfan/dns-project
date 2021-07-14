from django.urls import path

from . import views

urlpatterns = [
    path('create_cert', views.create_cert, name='create_cert'),
    path('get_cert', views.get_cert, name='get_cert'),
    path('init', views.init, name='init'),
    path('say_hello', views.say_hello, name='say_hello'),
]
