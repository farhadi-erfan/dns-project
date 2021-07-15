from django.urls import path

from . import views

urlpatterns = [
    path('request_cert', views.request_cert, name='request_cert'),
    path('view_cert', views.view_cert, name='view_cert'),
    path('delegate', views.delegate, name='delegate'),
    path('exchange', views.exchange, name='exchange'),
]
