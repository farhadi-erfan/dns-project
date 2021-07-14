# Create your views here.
import json

# Create your views here.
import requests
from django.http import JsonResponse

from dns_project.utils import request_cert_from_ca, view_ca_cert
from merchant.models import Merchant, Transaction


def request_cert(request):
    bank = Merchant.load()
    certs = request_cert_from_ca('merchant')
    bank.public_key = certs['public_key']
    bank.private_key = certs['private_key']
    bank.certificate = certs['certificate']
    bank.save()
    return JsonResponse(certs)


def view_cert(request):
    name = json.loads(request.body).get('name', None)
    data = view_ca_cert(name, 'merchant')
    url = 'https://127.0.0.1:8090/ca/get_cert'
    return JsonResponse(data=data)


def payment_answer(request):
    body = json.loads(request.body)
    status = body['status']
    tid = body['transaction-id']
    transaction = Transaction.objects.filter(id=tid).first()
    if status.lower() == 'ok':
        transaction.status = Transaction.Status.SUCCESS
    else:
        transaction.status = Transaction.Status.FAILURE
    transaction.save()
    return JsonResponse({'status': 'ok'})


def buy(request):
    body = json.loads(request.body)
    buyer = body['buyer']
    value = body['value']
    transaction = Transaction.objects.create(buyer=buyer, amount=value)

    url = 'https://127.0.0.1:8090/user/payment_req'
    r = requests.post(url, {'payer': buyer, 'merchant': Merchant.load().public_key, 'value': value,
                            'transaction-id': transaction.id},
                      verify=False)
    return JsonResponse({'status': 'ok'})


def sign_up(request):
    url = 'https://127.0.0.1:8090/bank/authenticate'
    r = requests.post(url, {'username': Merchant.load().public_key},
                      verify=False)
    merchant = Merchant.load()
    merchant.token = r.json().get('token')
    merchant.save()
    return JsonResponse({'status': 'ok'})
