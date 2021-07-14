from cryptography.hazmat.primitives import serialization
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_ca.models import CertificateAuthority, Certificate

from dns_project.utils import *

NAME = 'ca'


@csrf_exempt
def init(request):
    private_key, public_key, cert = create_ca(NAME)
    save_keys(private_key, public_key, cert, NAME)
    with open(f"../keys/{NAME}.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    return JsonResponse(data={'success': True,
                              'private_key': codecs.decode(serialize_private_key(private_key)),
                              'public_key': codecs.decode(serialize_public_key(public_key)),
                              'certificate': codecs.decode(serialize_cert(cert))})


@csrf_exempt
def create_cert(request):
    # TODO - place symmetric decryption on POST data here.
    if request.method != 'POST':
        return JsonResponse({
            'error': 'only post requests allowed'
        })
    name = request.POST.get('name', 'example')
    csr = deserialize_csr(request.POST.get('csr', None))
    ca_private_key, ca_public_key, ca_cert = load_keys_as_cryptography(NAME)
    cert = sign_csr(csr, ca_cert, ca_private_key)

    save_cert(cert, f'{NAME}-{name}')
    return JsonResponse({'success': True,
                         'certificate': codecs.decode(serialize_cert(cert))})


@csrf_exempt
def get_cert(request):
    if request.method != 'POST':
        return JsonResponse({
            'error': 'only post requests allowed'
        })
    name = request.POST.get('name', None)
    cert = load_cert_as_cryptography(f'{NAME}-{name}')
    return JsonResponse({'success': cert is not None,
                         'certificate': codecs.decode(serialize_cert(cert))})


def say_hello(request):
    rand = request.POST.get('hi')
    return JsonResponse({'hello': rand})
