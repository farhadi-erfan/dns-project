from django.urls import path

from . import views

urlpatterns = [
    path('create_cert', views.request_cert, name='create_cert'),
    path('get_cert', views.view_cert, name='get_cert'),
    path('payment_req', views.payment_req, name='payment_req'),
    path('buy', views.buy, name='buy'),
]
