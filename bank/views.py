import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from dns_project.utils import *


def request_cert(request):
    return JsonResponse(request_cert_from_ca('bank'))


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


