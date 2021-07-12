from cryptography.hazmat.primitives import serialization
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_ca.models import CertificateAuthority, Certificate
from dns_project.utils import *


@csrf_exempt
def create_cert(request):
    name = request.POST.get('name', 'example')
    print(request.POST.get('csr'))
    csr = deserialize_csr(request.POST.get('csr', None))
    # csr = load_csr(name)
    ca = CertificateAuthority.objects.all().first()
    cert = Certificate.objects.create_cert(ca, csr, subject=f'/CN={name}.com')
    save_cert(cert, name)
    return JsonResponse({'success': True, 'certificate': serialize_ca_certificate(cert)})


@csrf_exempt
def get_cert(request):
    name = request.POST.get('name', None)
    print(name)
    cert = Certificate.objects.filter(cn=f'{name}.com').first()
    return JsonResponse({'success': cert is not None, 'certificate': serialize_ca_certificate(cert)})
