
import OpenSSL.crypto
from OpenSSL import SSL, crypto
import socket
import certifi
import pem
import fnmatch
import urllib

from datetime import datetime

# Cert Paths
TRUSTED_CERTS_PEM = certifi.where()


def get_cert_chain(target_domain):
    '''
    This function gets the certificate chain from the provided
    target domain. This will be a list of x509 certificate objects.
    '''
    # Set up a TLS Connection
    dst = (target_domain.encode('utf-8'), 443)
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    s = socket.create_connection(dst)
    s = SSL.Connection(ctx, s)
    s.set_connect_state()
    s.set_tlsext_host_name(dst[0])

    # Send HTTP Req (initiates TLS Connection)
    s.sendall('HEAD / HTTP/1.0\n\n'.encode('utf-8'))
    s.recv(16)

    # Get Cert Meta Data from TLS connection
    test_site_certs = s.get_peer_cert_chain()
    s.close()
    return test_site_certs


############### Add Any Helper Functions Below

def print_chain_details(certs):
    for cert in certs:
        subject = cert.get_subject()
        issuer = cert.get_issuer()
        not_before = cert.get_notBefore().decode('utf-8')
        not_after = cert.get_notAfter().decode('utf-8')
        serial_number = cert.get_serial_number()
        version = cert.get_version()

        print(f"Subject: {subject}")
        print(f"Issuer: {issuer}")
        print(f"Valid From: {not_before}")
        print(f"Valid To: {not_after}")
        print(f"Serial Number: {serial_number}")
        print(f"Version: {version}")
        print("\n")


def getRootCerts():
    with open(certifi.where(), 'rb') as f:
        pem_data = f.read()

    certs = pem_data.split(b'-----END CERTIFICATE-----')
    certs = [cert + b'-----END CERTIFICATE-----' for cert in certs if cert.strip()]

    root_certs = []
    for cert in certs:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        root_certs.append(cert)

    return root_certs


def checkSAN(cert, domain):
    san_list = []
    for i in range(cert.get_extension_count()):
        ext = cert.get_extension(i)
        if ext.get_short_name() == b'subjectAltName':
            san_list = str(ext).split(", ")
            break

    if san_list:
        for san in san_list:
            if san.startswith("DNS:"):
                san = san.split(":", 1)[1]

            if san.count('.') != domain.count('.'):
                continue

            if fnmatch.fnmatch(domain, san):
                return True
    else:
        subject = cert.get_subject()
        common_name = subject.CN
        if fnmatch.fnmatch(domain, common_name):
            return True

    return False


##############################################

def x509_cert_chain_check(target_domain: str) -> bool:
    '''
    This function returns true if the target_domain provides a valid
    x509cert and false in case it doesn't or if there's an error.
    '''
    # TODO: Complete Me!

    store = OpenSSL.crypto.X509Store()
    root_certs = getRootCerts()
    for root_cert in root_certs:
        store.add_cert(root_cert)

    try:
        chain = get_cert_chain(target_domain)

        print_chain_details(chain)

        for intermediate_certs in chain[1:]:
            store.add_cert(intermediate_certs)

        end_entity = chain[0]

        if not checkSAN(end_entity, target_domain):
            return False

        store_ctx = crypto.X509StoreContext(store, end_entity)
        store_ctx.verify_certificate()
        return True

    except crypto.X509StoreContextError as e:
        print("failed:", e)
        return False


if __name__ == "__main__":
    # Standalone running to help you test your program
    print("Certificate Validator...")
    # target_domain = input("Enter TLS site to validate: ")
    target_domain = "facebook.com"
    print("Certificate for {} verifed: {}".format(target_domain, x509_cert_chain_check(target_domain)))
