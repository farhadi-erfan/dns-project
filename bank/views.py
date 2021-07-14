import random

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
from dns_project.utils import *
import requests
import codecs
import json


@csrf_exempt
def request_cert(request):
    private_key, csr = create_csr('bank')
    url = 'https://127.0.0.1:8090/ca/create_cert'
    data = {'name': 'bank', 'csr': serialize_csr(csr)}
    # TODO - place symmetric encryption here on data
    r = requests.post(url, data, verify=False)
    if r.json().get('success', False) is True:
        cert = deserialize_cert(r.json()['certificate'])
        save_cert(cert, 'bank')
        public_key = cert.public_key()
        if test_keys(private_key, public_key):
            pass
        return JsonResponse(data={'success': True,
                                  'private_key': codecs.decode(serialize_private_key(private_key)),
                                  'public_key': codecs.decode(serialize_public_key(public_key)),
                                  'certificate': codecs.decode(cert.public_bytes(serialization.Encoding.PEM))})
    return JsonResponse(data=r.json())


@csrf_exempt
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
        url = 'https://127.0.0.1:8090/bank/say_hi'
        r = requests.post(url, {'hi': random.random()},
                          verify='../keys/ca.pem', cert=('../keys/bank.crt', '../keys/bank.key'))
        return JsonResponse(data=r.json())
    else:
        return JsonResponse({'hello': hi})