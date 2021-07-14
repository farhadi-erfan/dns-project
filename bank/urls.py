from django.urls import path

from . import views

urlpatterns = [
    path('request_cert', views.request_cert, name='request_cert'),
    path('view_cert', views.view_cert, name='view_cert'),
    path('say_hi', views.say_hi, name='view_hi')
]
