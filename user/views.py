# Create your views here.
import json

import requests
from django.http import JsonResponse

from dns_project.utils import request_cert_from_ca, view_ca_cert
from user.models import Buyer


def request_cert(request):
    bank = Buyer.load()
    certs = request_cert_from_ca('buyer')
    bank.public_key = certs['public_key']
    bank.private_key = certs['private_key']
    bank.certificate = certs['certificate']
    bank.save()
    return JsonResponse(certs)


def view_cert(request):
    name = json.loads(request.body).get('name', None)
    data = view_ca_cert(name, 'buyer')
    return JsonResponse(data=data)


def payment_req(request):
    body = json.loads(request.body)
    payer = body['payer']
    merchant = body['merchant']
    value = body['value']
    tid = body['transaction-id']

    if Buyer.load().public_key != payer:
        return JsonResponse({'status': 'wrong-user'}, status=404)

    url = 'https://127.0.0.1:8090/bank/authenticate'
    r = requests.post(url, {'username': Buyer.load().public_key},
                      verify=False)

    if r.status_code != 200:
        return JsonResponse({'status': 'failure'}, status=404)

    url = 'https://127.0.0.1:8090/bank/payment'
    r = requests.post(url, {'payer': payer, 'merchant': merchant, 'value': value, 'transaction-id': tid,
                            'token': r.json().get('token')},
                      verify=False)

    if r.status_code != 200:
        return JsonResponse({'status': 'failure'}, status=404)
    return JsonResponse({'status': 'ok'})


def buy(request):
    return None
