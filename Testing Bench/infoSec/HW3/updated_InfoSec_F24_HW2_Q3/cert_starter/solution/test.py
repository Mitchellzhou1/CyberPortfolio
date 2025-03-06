#!/usr/bin/python3

from OpenSSL import SSL, crypto
import socket
import certifi
import pem
import fnmatch
import urllib
from datetime import datetime

# Cert Paths
TRUSTED_CERTS_PEM = certifi.where()


def print_certificate_details(cert):
    '''
    Print the details of an X509 certificate object.
    '''
    # Get and print the subject (owner of the certificate)
    subject = cert.get_subject()
    print(f"  Common Name (CN): {subject.CN}")


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


def check_domains(target_domain, cert):
    check_CN = False
    check_SAN = False

    cert_domain = cert.get_subject().CN
    # PART 1: CHECK THE CN
    if cert_domain.startswith('*.'):
        # CHECKS THE BASE DOMAIN
        base_domain = cert_domain[2:]  # Strip the "*." to get the base domain
        if base_domain.count(".") == target_domain.count("."):
            if target_domain == base_domain:
                check_CN = True
            else:
                # CHECK SUBDOMAINS
                check_SAN = fnmatch.fnmatch(target_domain, base_domain)

    if not check_CN:
        # PART 2: CHECK THE SAN
        san = cert.get_extension_count()
        for i in range(san):
            ext = cert.get_extension(i)
            if "subjectAltName" in str(ext.get_short_name()):
                san_list = str(ext).split(", ")
                for san_entry in san_list:
                    if san_entry.startswith("DNS:"):
                        san_domain = san_entry[4:]
                        if 'youtube' in san_domain:
                            1
                        if san_domain.count(".") == target_domain.count(".") and fnmatch.fnmatch(target_domain,
                                                                                                  san_domain):
                            check_SAN = True
                            break
    return check_CN or check_SAN


def check_root(root, trusted_certs):
    '''
    Check if the root certificate is trusted.
    '''
    for trusted_cert in trusted_certs:
        if trusted_cert.get_subject().CN:
            if trusted_cert.get_subject() == root.get_subject() or trusted_cert.get_subject() == root.get_issuer():
                return True
    return False


############### Add Any Helper Functions Below

##############################################

def x509_cert_chain_check(target_domain: str) -> bool:
    '''
    This function returns true if the target_domain provides a valid
    x509cert and false in case it doesn't or if there's an error.
    '''
    # TODO: Complete Me!

    cert_chain = get_cert_chain(target_domain)

    # for cert in cert_chain:
    #     print_certificate_details(cert)
    trusted_certificates = pem.parse_file(TRUSTED_CERTS_PEM)
    trusted_certificates = [crypto.load_certificate(crypto.FILETYPE_PEM, trusted_certificate.as_bytes()) for
                            trusted_certificate in trusted_certificates]

    # function below is from the black hat slides
    store = crypto.X509Store()
    website_root_cert = cert_chain[-1]
    # i asked github copilot extension to write me correct the code below for addign certificate to the store i just made
    # for i in trusted_certificates:
    #     print(i.get_subject().CN)

    for trusted_certificate in trusted_certificates:
        store.add_cert(trusted_certificate)

    leaf_cert = cert_chain[0]

    for cert in cert_chain[1:]:
        store.add_cert(cert)

    try:
        store_ctx = crypto.X509StoreContext(store, leaf_cert)
        store_ctx.verify_certificate()
    except Exception as e:
        # print(target_domain, "Error verifying certificate")
        return False

    if not check_domains(target_domain, leaf_cert):
        print("Failed my domain function")
        return False

    if not check_root(website_root_cert, trusted_certificates):
        return False

    return True

    # pass


if __name__ == "__main__":
    # Standalone running to help you test your program
    print("Certificate Validator...")
    # target_domain = input("Enter TLS site to validate: ")
    target_domain = "youtube.com"
    print("Certificate for {} verifed: {}".format(target_domain, x509_cert_chain_check(target_domain)))

# my old logic
# code for balidating chain (x+1)
#     if len(cert_chain) >= 2:
#         #at least 2 (leaf & intermediate)
#         cert = cert_chain[0]
# #tihs one is for intermediate certificate
#         issuer_cert = cert_chain[1]
#         store_ctx = crypto.X509StoreContext(store, issuer_cert)
#         store_ctx.verify_certificate()

#     if len(cert_chain)>= 3:
#         # at least 3 (leaf, intermediate, root)
#         #tihs one is for intermediate certificate
#         cert = cert_chain[1]
#         # this is root certificate
#         issuer_cert = cert_chain[2]
#         store_ctx = crypto.X509StoreContext(store, issuer_cert)
#         store_ctx.verify_certificate()

#     if len(cert_chain) >= 4:
#         #tihs one is for intermediate certificate
#         cert = cert_chain[2]
#         issuer_cert = cert_chain[3]
#         store_ctx = crypto.X509StoreContext(store, issuer_cert)
#         store_ctx.verify_certificate()

# Verify the root certificate
# i got this code from the blackhat slides
# if len(cert_chain) >= 1:
# root_cert = cert_chain[-1]
# store_ctx = crypto.X509StoreContext(store, root_cert)
# store_ctx.verify_certificate()
