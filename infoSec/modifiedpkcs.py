#!/usr/bin/python3 -u
import json
import sys
import time
import random
from Crypto.Cipher import AES

cookiefile = '{"username": "guest", "expires": "2000-01-07", "is_admin": "false"}'
flag = 'flag.txt'
key = '2'*32

welcome = "Welcome to Secure Encryption Service version 1.{}".format(random.randint(0, 99))

def xor_strings(s1, s2):
    hex_pairs1 = [s1[i:i + 2] for i in range(0, len(s1), 2)]
    hex_pairs2 = [s2[i:i + 2] for i in range(0, len(s2), 2)]
    xor_result = []
    for h1, h2 in zip(hex_pairs1, hex_pairs2):
        xor_value = int(h1, 16) ^ int(h2, 16)
        xor_result.append(f'{xor_value:02x}')

    return ''.join(xor_result)


def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)


def isvalidpad(s):
    return s[-1] * s[-1:] == s[-(s[-1]):]


def unpad(s):
    return s[:-(s[len(s) - 1])]


def encrypt(m):
    IV = b"This is an IV456"
    cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, IV)
    return IV.hex() + (cipher.encrypt(pad(m).encode("utf8"))).hex()

def decryption(m):
    cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, bytes.fromhex(m[0:32]))
    return cipher.decrypt(bytes.fromhex(m[32:]))

def get_cookie():
    return encrypt(cookiefile)

def test_cookie(cookie2):
    cookie2decoded = decryption(cookie2)
    if isvalidpad(cookie2decoded):
        return True
    else:
        return False


def reencrypt_blocks(plaintext_bytes, intermediary_values):

    plaintext_blocks = [plaintext_bytes[i:i + 16] for i in range(0, len(plaintext_bytes), 16)]
    intermediary_blocks = [intermediary_values[i:i + 16] for i in range(0, len(intermediary_values), 16)]

    ciphertext_blocks = []

    for p_block, i_block in zip(plaintext_blocks, intermediary_blocks):
        ciphertext_block = bytes([p ^ i for p, i in zip(p_block, i_block)])
        ciphertext_blocks.append(ciphertext_block)

    # Return the concatenated ciphertext
    return b''.join(ciphertext_blocks)


def final_test(cookie2):
    cookie2decoded = decryption(cookie2)

    if isvalidpad(cookie2decoded):
        d = json.loads(unpad(cookie2decoded).decode('utf-8'))
        # print("username: " + d["username"])
        # print("Admin? " + d["is_admin"])
        # exptime = time.strptime(d["expires"], "%Y-%m-%d")
        # if exptime > time.localtime():
        #     print("Cookie is not expired", flush=True)
        # else:
        #     print("Cookie is expired", flush=True)
        # if d["is_admin"] == "true" and exptime > time.localtime():
        #     print("The flag is: " + flag, flush=True)
        return True
    else:
        # print("invalid padding", flush=True)
        return False

# # Input data
# plaintext_hex = "7b22757365726e616d65223a20227573657232323232222c202269735f61646d696e223a202246616c7365222c2265787069726573223a2022323032342d30392d3237227d0b0b0b0b0b0b0b0b0b0b0b"
# intermediary_hex = "2f4a1c00451b1d410c0b0273761640457be265e9fa2a230c5cd848c9ea216553156fef0e8373fb6c48d5ab303d7d9dafc4fd387b0b1c00d97e10838965c6881e2776bc5e5b5ea6897bcdbcbd6ec27419"
# ciphertext_last = get_cookie()[-32:]
#
#
# # Convert hex to bytes
# plaintext_bytes = bytes.fromhex(plaintext_hex)
# intermediary_values = bytes.fromhex(intermediary_hex)
#
# # # Re-encrypt
# ciphertext = reencrypt_blocks(plaintext_bytes, intermediary_values)
# #
# # # Output the result
# print(ciphertext.hex())
# print(get_cookie())
# #
# final_test(ciphertext.hex() + ciphertext_last)