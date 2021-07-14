import codecs
import datetime
import uuid

from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from OpenSSL import crypto


# --- primary usages ---


def create_private_key(name):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    save_private_key(key, name)
    return key


def create_ca(name, expiration_delta=500):
    private_key = create_private_key(name)
    public_key = private_key.public_key()

    certificate = x509.CertificateBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u'dns-CA'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'g-12'),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u'Default CA Deployment'),
    ])).issuer_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u'dns-CA'),
    ])).not_valid_before(
        datetime.datetime.today() - datetime.timedelta(days=1)
    ).not_valid_after(
        datetime.datetime.now() + datetime.timedelta(days=expiration_delta)
    ).serial_number(
        int(uuid.uuid4())
    ).public_key(
        public_key
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).sign(
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
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(f"{name}.com"),
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
