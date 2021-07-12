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
    url = 'http://127.0.0.1:8090/ca/create_cert'
    r = requests.post(url, {'name': 'bank', 'csr': serialize_csr(csr)})
    if r.json().get('success', False) is True:
        cert = deserialize_certificate(r.json()['certificate'])
        public_key = cert.public_key()
        if test_keys(private_key, public_key):
            return JsonResponse(data={'success': True,
                                      'private_key': codecs.decode(serialize_private_key(private_key)),
                                      'public_key': serialize_public_key(public_key)})
    return JsonResponse(data=r.json())


@csrf_exempt
def view_cert(request):
    name = json.loads(request.body).get('name', None)
    url = 'http://127.0.0.1:8090/ca/get_cert'
    r = requests.post(url, {'name': name})
    if r.json().get('success', False) is True:
        cert = deserialize_certificate(r.json()['certificate'])
        public_key = cert.public_key()
        return JsonResponse(data={'success': True,
                                  'public_key': serialize_public_key(public_key)})
    return JsonResponse(data=r.json())
