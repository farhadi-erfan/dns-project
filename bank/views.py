import json
from random import random

from django.db.transaction import atomic
from django.http import JsonResponse

from bank.models import Transaction, Account, Bank
from dns_project.utils import *


def request_cert(request):
    bank = Bank.load()
    certs = request_cert_from_ca('bank')
    bank.public_key = certs['public_key']
    bank.private_key = certs['private_key']
    bank.certificate = certs['certificate']
    bank.save()
    return JsonResponse(certs)


def view_cert(request):
    name = json.loads(request.body).get('name', None)
    url = 'https://127.0.0.1:8090/ca/get_cert'
    r = requests.post(url, {'name': name}, verify=False)
    if r.json().get('success', False) is True:
        cert = deserialize_cert(r.json()['certificate'])
        save_cert(cert, f'bank-{name}')
        public_key = cert.public_key()
        return JsonResponse(data={'success': True,
                                  'public_key': codecs.decode(serialize_public_key(public_key))})
    return JsonResponse(data=r.json())


def say_hi(request):
    hi = request.POST.get('hi', None)
    if hi is None:
        url = 'https://127.0.0.1:8090/bank/say_hi?hi=h'
        r = requests.get(url, verify='../keys/ca.crt', cert=('../keys/bank.crt', '../keys/bank.key')
                         )
        return JsonResponse(data=r.json())
    else:
        return JsonResponse({'hello': hi})


@atomic
def payment(request):
    body = json.loads(request.body)
    payer = body['payer']
    merchant = body['merchant']
    value = body['value']
    tid = body['transaction-id']
    if Transaction.objects.filter(tid=tid).exists():
        return JsonResponse({
            'status': 'duplicate'
        }, status=400)

    url = 'https://127.0.0.1:8090/blockchain/exchange'
    r = requests.post(url, {'sender': payer, 'receiver': Bank.load().public_key, 'value': value, 'nonce': random()},
                      verify=False)
    if r.status_code != 200:
        return JsonResponse(data=r.json(), status=r.status_code)
    Transaction.objects.create(source=payer, destination=merchant, amount=value, tid=tid)
    merchant_account = Account.objects.get(username=merchant)
    merchant_account.credit += value
    merchant_account.save()
    payer_account = Account.objects.get(username=payer)
    payer_account.credit -= value
    payer_account.save()
    return JsonResponse({
        'status': 'ok',
        'transaction-id': tid
    })
