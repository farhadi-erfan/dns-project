from django.urls import path

from . import views

urlpatterns = [
    path('payment_answer', views.payment_answer, name='payment_answer'),
    path('buy', views.buy, name='buy'),
    path('create_cert', views.request_cert, name='create_cert'),
    path('get_cert', views.view_cert, name='get_cert'),
    path('sign_up', views.sign_up, name='sign_up'),
]
