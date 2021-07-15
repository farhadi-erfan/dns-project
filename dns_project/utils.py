import codecs
import datetime
import subprocess
import uuid

import requests
from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID


# --- primary usages ---


def create_private_key(name):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    save_private_key(key, name)
    return key


def create_ca(name, expiration_delta=500):
    private_key = create_private_key(name)
    public_key = private_key.public_key()
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'g-12'),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u'Default CA Deployment'),
        x509.NameAttribute(NameOID.COMMON_NAME, u'dns'),
    ])
    certificate = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).not_valid_before(
        datetime.datetime.today() - datetime.timedelta(days=1)
    ).not_valid_after(
        datetime.datetime.now() + datetime.timedelta(days=expiration_delta)
    ).serial_number(
        int(uuid.uuid4())
    ).public_key(
        public_key
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).add_extension(x509.SubjectAlternativeName(
        [x509.DNSName(u"localhost"), x509.DNSName(u"localhost:8090"), x509.DNSName("127.0.0.1")]),
        critical=False).sign(
        private_key=private_key, algorithm=hashes.SHA256(), backend=default_backend()
    )

    if isinstance(certificate, x509.Certificate):
        save_cert(certificate, name)
        return private_key, public_key, certificate
    return None, None, None


def sign_csr(csr, ca_cert, ca_private_key, expiration_delta=100):
    cert = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now() - datetime.timedelta(days=1)
    ).not_valid_after(
        datetime.datetime.now() + datetime.timedelta(days=expiration_delta)
    ).sign(
        private_key=ca_private_key, algorithm=hashes.SHA256(), backend=default_backend()
    )

    return cert


def create_csr(name):
    key = create_private_key(name)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"{name}"),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(f"{name}.com"),
            x509.DNSName(f"{name}"),
            x509.DNSName(f"dns"),
            x509.DNSName(f"localhost:8090"),
            x509.DNSName(f"localhost"),
            x509.DNSName(f"127.0.0.1"),
        ]),
        critical=False,
    ).sign(
        key, hashes.SHA256(), backend=default_backend()
    )

    save_csr(csr, name)
    return key, csr


# --- de/serialization ---


def serialize_cert(cert):
    return cert.public_bytes(serialization.Encoding.PEM)


def deserialize_cert(cert):
    return x509.load_pem_x509_certificate(codecs.encode(cert), default_backend())


def serialize_private_key(private_key):
    return private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                     format=serialization.PrivateFormat.TraditionalOpenSSL,
                                     encryption_algorithm=serialization.NoEncryption())


def serialize_public_key(public_key):
    return public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                   format=serialization.PublicFormat.SubjectPublicKeyInfo)


def serialize_csr(csr):
    return csr.public_bytes(encoding=serialization.Encoding.PEM)


def deserialize_csr(csr):
    return x509.load_pem_x509_csr(bytes(csr, 'utf-8'), default_backend())


# --- test ---


def test_keys(private_key, public_key):
    message = b'dns_project'
    ciphertext = public_key.encrypt(message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None
                                                          ))
    plaintext = private_key.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                             algorithm=hashes.SHA256(),
                                                             label=None))
    return plaintext == message


# --- save and load ---


def save_private_key(key, name):
    with open(f"../keys/{name}.key", "wb") as f:
        f.write(serialize_private_key(key))


def save_public_key(key, name):
    with open(f"../keys/{name}.pub", "wb") as f:
        f.write(serialize_public_key(key))


def save_csr(csr, name):
    with open(f"../keys/{name}.csr", "wb") as f:
        f.write(serialize_csr(csr))


def load_csr_as_cryptography(name):
    return x509.load_pem_x509_csr(open(f"../keys/{name}.csr", "rb").read(), default_backend())


def save_cert(cert, name):
    with open(f"../keys/{name}.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def load_cert_as_cryptography(name):
    return x509.load_pem_x509_certificate(open(f"../keys/{name}.crt", "rb").read(), default_backend())


def save_keys(private_key, public_key, cert, name):
    save_cert(cert, name)
    save_private_key(private_key, name)
    save_public_key(public_key, name)


def load_keys_as_cryptography(name):
    private_key = serialization.load_pem_private_key(open(f"../keys/{name}.key", "rb").read(),
                                                     backend=default_backend(), password=None)

    certificate = load_cert_as_cryptography(name)

    public_key = serialization.load_pem_public_key(open(f"../keys/{name}.pub", "rb").read(), backend=default_backend())

    if test_keys(private_key, certificate.public_key()) and test_keys(private_key, public_key):
        return private_key, public_key, certificate
    else:
        return None, None, None


def load_keys_as_crypto(name):
    with open(f'../keys/{name}.cert') as f:
        certificate = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
        certificate = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    with open(f'../keys/{name}.key') as f:
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
    with open(f'../keys/{name}.pub') as f:
        public_key = crypto.load_publickey(crypto.FILETYPE_PEM, f.read())

    if public_key == certificate.get_pubkey() and test_keys(private_key, public_key):
        return private_key, public_key, certificate
    else:
        return None, None, None


def request_cert_from_ca(name):
    private_key, csr = create_csr(name)
    url = 'https://127.0.0.1:8090/ca/create_cert'
    data = {'name': name, 'csr': serialize_csr(csr)}
    # TODO - place symmetric encryption here on data
    r = requests.post(url, data, verify=False)
    if r.json().get('success', False) is True:
        cert = deserialize_cert(r.json()['certificate'])
        save_cert(cert, 'bank')
        public_key = cert.public_key()
        if test_keys(private_key, public_key):
            pass
        return {'success': True,
                'private_key': codecs.decode(serialize_private_key(private_key)),
                'public_key': codecs.decode(serialize_public_key(public_key)),
                'certificate': codecs.decode(cert.public_bytes(serialization.Encoding.PEM))}
    return r.json()


def view_ca_cert(name, app):
    if not app:
        app = name
    url = 'https://127.0.0.1:8090/ca/get_cert'
    r = call(url, {'name': name})
    if r.json().get('success', False) is True:
        cert = deserialize_cert(r.json()['certificate'])
        save_cert(cert, f'{app}-{name}')
        public_key = cert.public_key()
        return {'success': True,
                'public_key': codecs.decode(serialize_public_key(public_key))}
    return r.json()


def call(url, data, verify=False):
    log('cert being checked')
    if not check_service_certificate(url.split('/')[3]):
        log('cert error')
        return None
    return requests.post(url, json=data, verify=False)


def log(message, title=''):
    print(f'--------->>> {title}: {message}')


def check_service_certificate(name):
    try:
        sp = subprocess.run(
            ['openssl', 'verify', '-CAfile', '../keys/ca.pem', f'../keys/ca-{name}.crt'])
        sp.check_returncode()
        return True
    except:
        return False


def ca_check(f):
    def inner(*args):
        check_service_certificate(args[0].path.split("/")[1])
        return f(*args)

    return inner
