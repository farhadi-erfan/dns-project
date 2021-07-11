from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import serialization


def load_keys(name):
    private_key = serialization.load_pem_private_key(open(f"../../keys/{name}.key", "rb").read(),
                                                     password=None, backend=default_backend())

    certificate = x509.load_pem_x509_certificate(open(f"../../keys/{name}.pub", "rb").read(), default_backend())

    public_key = certificate.public_key()

    return {'private_key': private_key,
            'public_key': public_key,
            'certificate': certificate}