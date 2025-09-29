#!/usr/bin/env python3
import sys
import time
from binascii import hexlify
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Random import get_random_bytes

# KEY = get_random_bytes(16)
# NONCE = get_random_bytes(8)

KEY = b'\xa7\x8aC\xdc\x0e?g\x12\xb5zj\xb3\xab>\t\x1e'
NONCE = b'\xe3\xa2/\x7f\xe43@\xfb'
MESSAGE = b"Greetings, Earthlings.1234567890123456789012345678901234567890123456789012345678901234000"

WELCOME = '''
     ,-.
    /   \\ 
   :     \\      ....*
   | . .- \\-----00''
   : . ..' \\''//
    \\ .  .  \\/
     \\ . ' . NASA Deep Space Listening Posts
  , . \\       \\     ~ Est. 1969 ~
,|,. -.\\       \\
    '.|| `-...__..-
      | | "We're always listening to you!"
     |__|
    /||\\\\
    //||\\\\
   // || \\\\
__//__||__\\\\__
'--------------'
'''


def main():
    # Print ASCII art and intro
    # sys.stdout.write(WELCOME)
    # sys.stdout.flush()
    # time.sleep(0.5)

    sys.stdout.write("\nConnecting to remote station")
    sys.stdout.flush()

    for i in range(5):
        sys.stdout.write(".")
        sys.stdout.flush()
        # time.sleep(0.5)

    sys.stdout.write("\n\n== BEGINNING TRANSMISSION ==\n\n")
    sys.stdout.flush()

    C = 0
    while True:
        ctr = Counter.new(64, prefix=NONCE, initial_value=C, little_endian=False)
        cipher = AES.new(KEY, AES.MODE_CTR, counter=ctr)
        ct = cipher.encrypt(MESSAGE)
        sys.stdout.write("%s\n" % hexlify(ct).decode())
        sys.stdout.flush()
        C += 1


if __name__ == "__main__":
    main()