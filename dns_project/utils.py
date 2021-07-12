import codecs

from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def create_private_key(name):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    with open(f"../keys/{name}.key", "wb") as f:
        f.write(serialize_private_key(key))
    return key


def create_csr(name):
    key = create_private_key(name)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        # x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        # x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        # x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        # x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        # x509.NameAttribute(NameOID.COMMON_NAME, u"mysite.com"),
    ])).add_extension(

        x509.SubjectAlternativeName([
            # Describe what sites we want this certificate for.
            x509.DNSName(f"{name}.com"),
        ]),

        critical=False,
        # Sign the CSR with our private key.
    ).sign(key, hashes.SHA256(), backend=default_backend())
    # Write our CSR out to disk.
    with open(f"../keys/{name}.csr", "wb") as f:
        f.write(serialize_csr(csr))
    return key, csr


def save_cert(cert, name):
    with open(f"../keys/{name}.pub", "wb") as f:
        f.write(cert.pub.encode(serialization.Encoding.PEM))


def load_csr(name):
    return x509.load_pem_x509_csr(open(f"../keys/{name}.csr", "rb").read(), default_backend())


def serialize_ca_certificate(cert):
    return codecs.decode(cert.pub.encode(serialization.Encoding.PEM), 'utf-8') if cert is not None else None


def serialize_private_key(private_key):
    return private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                     format=serialization.PrivateFormat.TraditionalOpenSSL,
                                     encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"))


def serialize_public_key(public_key):
    return codecs.decode(public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                 format=serialization.PublicFormat.SubjectPublicKeyInfo))


def serialize_csr(csr):
    return csr.public_bytes(encoding=serialization.Encoding.PEM)


def deserialize_csr(csr):
    return x509.load_pem_x509_csr(bytes(csr, 'utf-8'), default_backend())


def deserialize_certificate(cert):
    return x509.load_pem_x509_certificate(codecs.encode(cert), default_backend())


def test_keys(private_key, public_key):
    message = b'dns_project'
    ciphertext = public_key.encrypt(message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                          algorithm=hashes.SHA256(),
                                                          label=None
                                                          ))
    plaintext = private_key.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                             algorithm=hashes.SHA256(),
                                                             label=None))
    print(ciphertext)
    return plaintext == message


def load_keys(name):
    private_key = serialization.load_pem_private_key(open(f"../keys/{name}.key", "rb").read(),
                                                     password=b"passphrase", backend=default_backend())

    certificate = x509.load_pem_x509_certificate(open(f"../keys/{name}.pub", "rb").read(), default_backend())

    public_key = certificate.public_key()

    return {'private_key': private_key,
            'public_key': public_key,
            'certificate': certificate}
