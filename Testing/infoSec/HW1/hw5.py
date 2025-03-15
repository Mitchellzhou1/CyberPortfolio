from pwn import *
import multiprocessing

from modifiedpkcs import test_cookie, get_cookie



def get_blocks(s, size):
    return [s[i:i+size] for i in range(0, len(s), size)]

def xor_strings(s1, s2):
    hex_pairs1 = [s1[i:i + 2] for i in range(0, len(s1), 2)]
    hex_pairs2 = [s2[i:i + 2] for i in range(0, len(s2), 2)]
    xor_result = []
    for h1, h2 in zip(hex_pairs1, hex_pairs2):
        xor_value = int(h1, 16) ^ int(h2, 16)
        xor_result.append(f'{xor_value:02x}')

    return ''.join(xor_result)

def test_on_server(cookie):
    context.log_level = 'critical'
    context.proxy = (socks.SOCKS5, 'localhost', 8123)
    host = '192.168.2.99'
    port = 60032
    conn = remote(host, port)

    conn.recvuntil(b'What is your cookie?\n').decode()

    conn.sendline(cookie.encode('ascii')+b'\n')

    try:
        response = conn.recv(1024).decode()
        print('.', end='')
        conn.close()
        if 'invalid' not in response:
            return True
        return False
    except Exception:
        return True

def update_guess(guess_lst, intermediary, target):
    for indx in range(len(guess_lst) -1, len(guess_lst) - target - 1, -1):
        guess_lst[indx] = hex((target+1) ^ int(intermediary[indx], 16))[2:].zfill(2)
    return guess_lst

def reencrypt_blocks(plaintext_bytes, intermediary_values):
    # Split the plaintext into 16-byte blocks
    plaintext_bytes = bytes.fromhex(plaintext_bytes)
    intermediary_values = bytes.fromhex(intermediary_values)
    plaintext_blocks = [plaintext_bytes[i:i + 16] for i in range(0, len(plaintext_bytes), 16)]

    # Split intermediary values into 16-byte blocks
    intermediary_blocks = [intermediary_values[i:i + 16] for i in range(0, len(intermediary_values), 16)]

    # Initialize list for ciphertext blocks
    ciphertext_blocks = []

    # XOR each plaintext block with its corresponding intermediary block
    for p_block, i_block in zip(plaintext_blocks, intermediary_blocks):
        ciphertext_block = bytes([p ^ i for p, i in zip(p_block, i_block)])
        ciphertext_blocks.append(ciphertext_block)

    # Return the concatenated ciphertext
    return b''.join(ciphertext_blocks)

def convert_to_string(hex_string):
    bytes_data = bytes.fromhex(hex_string)
    ascii_text = bytes_data.decode('ascii')
    return ascii_text

def convert_to_hex(ascii_string):
    hex_string = ascii_string.encode('ascii').hex()
    return hex_string


def pkcs7_pad(text, block_size=16):
    # Calculate how much padding is needed
    padding_len = block_size - (len(text) % block_size)
    # Create the padding byte (repeated 'padding_len' times)
    padding = chr(padding_len) * padding_len
    # Return the text with the padding added
    return text + padding


def get_plaintext():
    start = time.time()
    # ciphertext = '5468697320697320616e204956343536c9231e442bef921941f54a268311950eb91cc2ffda59545073fe52c108c14cb7f925bccf1f402c869790a7e80614b22c2cd7fedcde70378aff83be9b78448602c714e50740c8d880c9364e031fc69c25'
    ciphertext = get_cookie() + '00' * 16
    print(ciphertext)
    original_blocks = get_blocks(ciphertext, 32)         # the IV was 16 bytes long

    original_intermediary = [''] * len(original_blocks)
    plaintext =  ''


    block_indx = len(original_blocks) - 2


    while block_indx > -1:
        unaltered_curr_block = get_blocks(original_blocks[block_indx], 2)
        altered_curr_block = get_blocks(original_blocks[block_indx], 2)
        test_padding = get_blocks(ciphertext, 32)[:block_indx+2]  # used to test the padding
        temp_intermediary = ['00'] * 16
        force_byte = 1
        cell_indx = 15

        while cell_indx > -1:
            hit_value = False
            correct_intermediary_value = unaltered_curr_block[cell_indx]

            for brute in range(256):
                # the first cell in the block MUST be 0x01. Sometimes I will hit the original value which doesn't
                # give me any useful information.
                if cell_indx == 15:
                    if brute == int(correct_intermediary_value, 16):
                        continue
                altered_curr_block[cell_indx] = hex(brute)[2:].zfill(2)
                guess_block = ''.join(altered_curr_block)
                test_padding[block_indx] = guess_block
                try:
                    # if test_on_server(''.join(test_padding)+"\n"):
                    if test_cookie(''.join(test_padding)+"\n"):
                        hit_value = True
                        print(hex(brute))
                        temp_intermediary[cell_indx] = hex(brute ^ force_byte)[2:].zfill(2)
                        altered_curr_block = update_guess(altered_curr_block, temp_intermediary, force_byte)
                        force_byte += 1
                        cell_indx -= 1
                        break
                except Exception:
                    hit_value = True
                    print(hex(brute))
                    temp_intermediary[cell_indx] = hex(brute ^ force_byte)[2:].zfill(2)
                    altered_curr_block = update_guess(altered_curr_block, temp_intermediary, force_byte)
                    force_byte += 1
                    cell_indx -= 1
                    break

            if not hit_value:
                write("doesn't work")
                print("NOOOO SOMETHING WENT WRONG MITCHHELL")

        plaintext = xor_strings(''.join(temp_intermediary), ''.join(unaltered_curr_block))+ plaintext
        print(plaintext)
        original_intermediary[block_indx] = ''.join(temp_intermediary)
        test_padding = test_padding[:-1]
        block_indx -= 1

    original_intermediary = ''.join(original_intermediary)
    print("Plaintext (hex):", plaintext)
    print("IntermediaryValues:", original_intermediary)

    end = time.time()

    print(f"program ran for {end - start}")

def re_encrypt_cookie():
    # new cookie decodes to {"username": "guest1", "expires": "2030-01-07", "is_admin": "true"}
    new_plaintext = '7b22757365726e616d65223a2022677565737431222c202265787069726573223a2022323033302d30312d3037222c202269735f61646d696e223a202274727565227d0d0d0d0d0d0d0d0d0d0d0d0d0d0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f'

    # original_plaintext = '7b22757365726e616d65223a20226775657374222c202265787069726573223a2022323030302d30312d3037222c202269735f61646d696e223a202266616c7365227d0d0d0d0d0d0d0d0d0d0d0d0d0d1f208cd5f5e3709987479a65ff3437e1'
    # intermediary_vals = '2f4a1c00451b1d410c0b0273761652437b80389c82ccf05a76fc22c6e01e03a47cb4b8342789513d865d250e573f663a68b9118f80277bdcc874ad58daddc86079a75988b323afcb9f14e962f7f4cf695e749c2d64e5ef78279337670223fc08'
    server_cookie = get_cookie() + '00' * 16
    original_cipher_blocks = get_blocks(server_cookie, 32)
    new_plaintext_blocks = get_blocks(new_plaintext, 32)
    new_intermediary = [''] * len(original_cipher_blocks)

    new_cookie = [''] * len(original_cipher_blocks)

    block_indx = len(original_cipher_blocks) - 2
    test_padding = get_blocks(server_cookie, 32) # used to test the padding

    while block_indx > -1:
        unaltered_curr_block = get_blocks(test_padding[block_indx], 2)
        altered_curr_block = get_blocks(test_padding[block_indx], 2)
        temp_intermediary = ['00'] * 16
        force_byte = 1
        cell_indx = 15

        while cell_indx > -1:
            hit_value = False
            correct_intermediary_value = unaltered_curr_block[cell_indx]

            for brute in range(256):
                # the first cell in the block MUST be 0x01. Sometimes I will hit the original value which doesn't
                # give me any useful information.
                if cell_indx == 15:
                    if brute == int(correct_intermediary_value, 16):
                        continue
                altered_curr_block[cell_indx] = hex(brute)[2:].zfill(2)
                guess_block = ''.join(altered_curr_block)
                test_padding[block_indx] = guess_block
                try:
                    # if test_on_server(''.join(test_padding)+"\n"):
                    if test_cookie(''.join(test_padding)+"\n"):
                        hit_value = True
                        print(hex(brute))
                        temp_intermediary[cell_indx] = hex(brute ^ force_byte)[2:].zfill(2)
                        altered_curr_block = update_guess(altered_curr_block, temp_intermediary, force_byte)
                        force_byte += 1
                        cell_indx -= 1
                        break
                except Exception:
                    hit_value = True
                    print(hex(brute))
                    temp_intermediary[cell_indx] = hex(brute ^ force_byte)[2:].zfill(2)
                    altered_curr_block = update_guess(altered_curr_block, temp_intermediary, force_byte)
                    force_byte += 1
                    cell_indx -= 1
                    break

            if not hit_value:
                print("NOOOO SOMETHING WENT WRONG MITCHHELL")


        print("new intermediary =", ''.join(temp_intermediary))
        new_intermediary[block_indx] = ''.join(temp_intermediary)
        test_padding = test_padding[:-1]
        test_padding[-1] = xor_strings(new_plaintext_blocks[block_indx], ''.join(temp_intermediary))
        new_cookie[block_indx] = test_padding[-1]
        block_indx -= 1

    original_intermediary = ''.join(new_intermediary)
    print("new Cookie (hex):", ''.join(new_cookie))
    print("IntermediaryValues:", original_intermediary)




re_encrypt_cookie()
server_cookie = '5468697320697320616e204956343536c9231e442bef921941f54a268311950eb91cc2ffda59545073fe52c108c14cb7f925bccf1f402c869790a7e80614b22c2cd7fedcde70378aff83be9b78448602c714e50740c8d880c9364e031fc69c25'
plaintext_server = '7b22757365726e616d65223a20226775657374222c202265787069726573223a2022323030302d30312d3037222c202269735f61646d696e223a202266616c7365227d0d0d0d0d0d0d0d0d0d0d0d0d0d'
intermediary_server = '2f4a1c00451b1d410c0b027376165243ac506a6607cfb07c39852354e662b734993ef0cfea69796042d362f62aed6c959056e3ae7b2d45e8b5aa87ca6075de5f49f583d1d37d3a87f28eb39675498b0f'
