from django.urls import path

from . import views

urlpatterns = [
    path('request_cert', views.request_cert, name='create_cert'),
    path('view_cert', views.view_cert, name='get_cert'),
    path('payment_req', views.payment_req, name='payment_req'),
    path('run_scenario', views.run_scenario, name='run_scenario'),
]
