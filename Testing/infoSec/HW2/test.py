import struct

# plaintext = b'username=nekomusume&groups=students,users,'
plaintext = input('What is the plaintext: ').strip().encode('utf-8')
server_hash = input("What is the server's hash: ").strip()
added = b'admins'

key_len = 16
plain_len = len(plaintext)

def add_padding(msg):
    len_orig = 8 * len(msg)
    msg = msg + b"\x80"

    while (len(msg) + 8) % 64 != 0:
        msg = msg + b"\x00"

    msg = msg + struct.pack(">Q", len_orig)
    return msg

def padding_value(msg):
    check = b'A' * 16 + msg
    padd_val = add_padding(check)
    padding = padd_val[len(check):]
    return padding

def new_sha_start_values(hash):
    val = [hash[i:i+8] for i in range(0, len(hash)-1, 8)]
    for i in range(len(val)):
        print(f'h{i} = 0x{val[i]}')


new_sha_start_values(server_hash)

padding1 = padding_value(plaintext)

payload = plaintext+padding1+added
padding2 = padding_value(payload)

print("Payload plaintext:", (payload).hex())
print("Enter this into the SHA.py with the starting values:\n", added+padding2)


