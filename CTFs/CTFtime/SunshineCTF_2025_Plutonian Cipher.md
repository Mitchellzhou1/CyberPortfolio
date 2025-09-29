# CTF Competition: Sunshine CTF

### CTF Name: Plutonian Crypto
**CTF Weight:** 437 points

<img width="470" height="518" alt="Screenshot from 2025-09-29 17-53-02" src="https://github.com/user-attachments/assets/78975213-86be-41f4-a4a3-261d43d3b80d" />


Worked on it with my teammate: Max Yin

Full writeup: `https://blog.bbtc33.com/sunshine-ctf-writeup-plutonian-cipher/`


solution script:
```
#! /usr/bin/python3
from pwn import *
import math

known = b"Greetings, Earthlings"
known_hex = b"4772656574696e67732c204561727468"
stream = ""


def hex_to_ascii(h):
    return bytes.fromhex(h).decode("ascii")

def xor_blocks(a: str, b: str) -> str:
    a_bytes = bytes.fromhex(a)
    b_bytes = bytes.fromhex(b)
    return bytes(x ^ y for x, y in zip(a_bytes, b_bytes)).hex()


def first_chunk(h: str) -> str:
    return h[:32]





##############COMMS

remote_flag = True
def get_ciphertext():
    if remote_flag:
        p = remote("chal.sunshinectf.games", 25403)
    else:
        p = process(["python3", "test.py"])

    p.recvuntil(b"==\n\n")
    output = []
    for i in range(27):
        output.append(p.recvline().decode("utf-8").strip())
    return output



############DECRYPT


############MAIN

if __name__ == "__main__":

    ctext_total = get_ciphertext()

    for chunk in ctext_total:
        chunk = first_chunk(chunk)
        stream += xor_blocks(known_hex.decode(), chunk)
        # print(stream)

    decrypt = xor_blocks(stream, ctext_total[0])
    print(hex_to_ascii(decrypt))




"""

4772656574696e67732c204561727468 -> 16 block plaintext
852a07929ff38472fbabc9ea20e5f935 -> 16 block cipher

c25862f7eb9aea158887e9af41978d5d -> 16 block keystream


4772656574696e67732c204561727468 -> 16 block plaintext
de44d213c0e13b27b59f2e19c986a0e5 -> 16 block cipher

9936b776b4885540c6b30e5ca8f4d48d -> 16 block keystream


852a07929ff38472fbabc9ea20e5f935f55fd911c7a66472f5873b6a9fccedbdbac842715ac43170499421ba7ef0a6a2a92f32463eee97058ba87b405d1107fe50f0778f103fe2ad2ccdd5d69679a6330c09f9a8ac48d9c9d1

"""
```
