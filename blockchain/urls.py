from django.urls import path

from . import views

urlpatterns = [
    path('delegate', views.delegate, name='delegate'),
    path('exchange', views.exchange, name='exchange'),
]
