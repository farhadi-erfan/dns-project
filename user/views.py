# Create your views here.
import json
import random

from django.http import JsonResponse

from bank.models import Bank
from dns_project.utils import request_cert_from_ca, view_ca_cert, call, log
from user.models import Buyer


def request_cert(request):
    model = Buyer.load()
    certs = request_cert_from_ca('buyer')
    model.public_key = certs['public_key']
    model.private_key = certs['private_key']
    model.certificate = certs['certificate']
    model.save()
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
    log(f'user payment req called with: {payer}, {merchant}, {value}, {tid}')

    if Buyer.load().public_key != payer:
        return JsonResponse({'status': 'wrong-user'}, status=404)

    url = 'https://127.0.0.1:8090/bank/authenticate'
    r = call(url, {'username': Buyer.load().public_key})
    log(f'auth called: {r}')

    if r.status_code != 200:
        return JsonResponse({'status': 'failure'}, status=404)

    url = 'https://127.0.0.1:8090/bank/payment'
    r = call(url, {'payer': payer, 'merchant': merchant, 'value': value, 'transaction-id': tid,
                   'token': r.json().get('token')})
    log(f'payment called: {r}')

    if r.status_code != 200:
        return JsonResponse({'status': 'failure'}, status=404)
    return JsonResponse({'status': 'ok'})


def run_scenario(request):
    body = json.loads(request.body)
    value = body.get('value', 10000)
    count = body.get('count', 1)
    deadline = body.get('deadline', '2022-12-12')
    log(f'run scenario called with value: {value}')
    url = 'https://127.0.0.1:8090/blockchain/delegate'
    r = call(url, {'pkm': Buyer.load().public_key, 'pkd': Bank.load().public_key, 'nonce': random.random(), 'policy': {
        'amount': value,
        'count': count,
        'time': deadline
    }})
    log(f'delegate request called result: {r}')
    url = 'https://127.0.0.1:8090/merchant/buy'
    r = call(url, {'buyer': Buyer.load().public_key, 'value': value})
    log(f'buy request called result: {r}')
    return JsonResponse({'status': 'ok'})
