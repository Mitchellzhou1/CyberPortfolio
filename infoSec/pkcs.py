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


def decrypt(m):
    cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, bytes.fromhex(m[0:32]))
    return cipher.decrypt(bytes.fromhex(m[32:]))


# flush output immediately
print(welcome)
print("Here is a sample cookie: " + encrypt(cookiefile))

# Get their cookie
print("What is your cookie?", flush=True)
cookie2 = sys.stdin.readline()
# decrypt, but remove the trailing newline first
cookie2decoded = decrypt(cookie2[:-1])
# cookie2decoded = '7b22757365726e616d65223a2022677565737431222c202265787069726573223a2022323033302d30312d3037222c202269735f61646d696e223a202274727565227d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d'
# cookie2decoded = bytes.fromhex(cookie2decoded)
if isvalidpad(cookie2decoded):
    d = json.loads(unpad(cookie2decoded).decode('utf-8'))
    print("username: " + d["username"])
    print("Admin? " + d["is_admin"])
    exptime = time.strptime(d["expires"], "%Y-%m-%d")
    if exptime > time.localtime():
        print("Cookie is not expired", flush=True)
    else:
        print("Cookie is expired", flush=True)
    if d["is_admin"] == "true" and exptime > time.localtime():
        print("The flag is: " + flag, flush=True)
else:
    print("invalid padding", flush=True)