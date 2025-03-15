#!/usr/bin/python3
import OpenSSL.crypto
from OpenSSL import SSL,crypto
import socket
import certifi
# import pem
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


def print_cert(chain):
    for cert in chain:
        subject = cert.get_subject()
        print(f"  Common Name (CN): {subject.CN} \t\tissueer: {cert.get_issuer()}")



############### Add Any Helper Functions Below

def getRootCerts():
    with open(TRUSTED_CERTS_PEM, 'rb') as f:
        pem_data = f.read()

    certs = pem_data.split(b'-----END CERTIFICATE-----')
    certs = [cert + b'-----END CERTIFICATE-----' for cert in certs if cert.strip()]

    root_certs = []
    for cert in certs:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        root_certs.append(cert)

    return root_certs

def checkDomain(cert, domain):
    san_list = []

    common_name = cert.get_subject().CN
    base = common_name
    if '*.' in common_name:
        base = common_name[2:]
    if base.count('.') != domain.count('.') and fnmatch.fnmatch(domain, base):
        return True

    # Checking SAN if CN didn't work
    for i in range(cert.get_extension_count()):
        ext = cert.get_extension(i)
        if ext.get_short_name() == b'subjectAltName':
            san_list = str(ext).split(", ")
            break

    if san_list:
        for san in san_list:
            if san[:3] == "DNS":
                san = san.split(":", 1)[1]

            if san.count('.') != domain.count('.'):
                continue

            if fnmatch.fnmatch(domain, san):
                return True

    return False

def checkRoot(myroots, website_root):
    for root_cert in myroots:
        if root_cert.get_subject() == website_root.get_subject() \
                or root_cert.get_issuer() == website_root.get_issuer():
            return True
    return False

##############################################

def x509_cert_chain_check(target_domain: str) -> bool:
    '''
    This function returns True if the target_domain provides a valid
    X.509 certificate and False if it doesn't, or if there's an error.
    It also ensures that the root certificate is trusted.


    I Followed the following code structure from the black hat Youtube talk:
        store = OpenSSL.crypto.X509Store()
        store.add_cert(root_cert)

        store_ctx = OpenSSL.crypto.X509StoreContext(store, parsed_chain)
        store_ctx.verify_certificate()
        store.add_cert(parsed_chain)

        store_ctx = OpenSSL.crypto.X509StoreContext(store, end_entity_cert)
        store_ctx.verify_certificate()
    '''
    store = crypto.X509Store()
    my_root_certs = getRootCerts()
    for root_cert in my_root_certs:
        store.add_cert(root_cert)


    try:
        chain = get_cert_chain(target_domain)
        print_cert(chain)

        end_entity = chain[0]
        website_root = chain[-1]
        if not checkDomain(end_entity, target_domain):
            print(f"Domain not found {target_domain}")
            return False

        if not checkRoot(my_root_certs, website_root):
            print(f"Root not in my system: {website_root.get_subject()}")
            return False

        for intermed_cert in chain[1:]:
            store.add_cert(intermed_cert)
        store_ctx = crypto.X509StoreContext(store, end_entity)
        store_ctx.verify_certificate()
        return True

    except Exception as e:
        return False



if __name__ == "__main__":
    
    # Standalone running to help you test your program
    print("Certificate Validator...")
    # target_domain = input("Enter TLS site to validate: ")
    target_domain = "facebook.com"
    print("Certificate for {} verifed: {}".format(target_domain, x509_cert_chain_check(target_domain)))
