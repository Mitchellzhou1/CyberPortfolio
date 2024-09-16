
from infoSec.modifiedpkcs import get_cookie, xor_strings, decryption, final_test

import binascii

def get_blocks(s, size):
    return [s[i:i+size] for i in range(0, len(s), size)]

cipher = get_cookie() + '00' * 16
plaintext_hex = "7b22757365726e616d65223a20226775657374222c202265787069726573223a2022323030302d30312d3037222c202269735f61646d696e223a202266616c7365227d0d0d0d0d0d0d0d0d0d0d0d0d0d1f208cd5f5e3709987479a65ff3437e1"
intermediary_hex = "2f4a1c00451b1d410c0b0273761652437b80389c82ccf05a76fc22c6e01e03a47cb4b8342789513d865d250e573f663a68b9118f80277bdcc874ad58daddc86079a75988b323afcb9f14e962f7f4cf69"
ciphertext_last = get_cookie()[-32:]
#
# server_cookie = '5468697320697320616e204956343536c9231e442bef921941f54a268311950eb91cc2ffda59545073fe52c108c14cb7f925bccf1f402c869790a7e80614b22c2cd7fedcde70378aff83be9b78448602c714e50740c8d880c9364e031fc69c25'
# plaintext_server = '7b22757365726e616d65223a20226775657374222c202265787069726573223a2022323030302d30312d3037222c202269735f61646d696e223a202266616c7365227d0d0d0d0d0d0d0d0d0d0d0d0d0d'
# intermediary_server = '2f4a1c00451b1d410c0b027376165243ac506a6607cfb07c39852354e662b734993ef0cfea69796042d362f62aed6c959056e3ae7b2d45e8b5aa87ca6075de5f49f583d1d37d3a87f28eb39675498b0f'
#

decrypt = xor_strings(cipher, intermediary_hex)
print(binascii.unhexlify(decrypt))
print(binascii.unhexlify(plaintext_hex))
print("plaintext == decrypt", plaintext_hex==decrypt)


intermediary_total = '2f4a1c00451b1d410c0b0273761652437b80389c82ccf05a76fc22c6e01e03a47cb4b8342789513d865d250e573f663a68b9118f80277bdcc874ad58daddc86079a75988b323afcb9f14e962f7f4cf695e749c2d64e5ef78279337670223fc08'
new_cipher = xor_strings(''.join(plaintext_hex) + '00' * 16, intermediary_total)

print(new_cipher)
print(decryption(new_cipher))


# n_plaintext_hex = "7b22757365726e616d65223a20226775657374222c202265787069726573223a2022323030302d30312d3037222c202269735f61646d696e223a202274616c7365227d0d0d0d0d0d0d0d0d0d0d0d0d0d"
#
# plain_blocks = get_blocks(plaintext_hex, 2)
# n_plaintext_hex = get_blocks(n_plaintext_hex, 2)
# intermediary_hex = get_blocks(intermediary_total, 2)
#
# for i in range(len(n_plaintext_hex)):
#     if plain_blocks[i] != n_plaintext_hex[i]:
#         intermediary_total = ''.join(intermediary_hex) + last_intermediary
#         new_cipher = xor_strings(''.join(n_plaintext_hex) + '0f' * 16, intermediary_total)
#         for j in range(256):
#             new_cipher = get_blocks(new_cipher, 2)
#             new_cipher[i] = hex(j)[2:].zfill(2)
#             new_cipher = ''.join(new_cipher)
#             print(decryption(new_cipher))
#             try:
#                 if final_test(new_cipher) and new_cipher != cipher:
#                     print(new_cipher)
#                     print(decryption(new_cipher))
#                     break
#             except:
#                 continue
#











#
# print(binascii.unhexlify(decrypt))
# print(binascii.unhexlify(n_plaintext_hex))
# new_cipher = xor_strings(''.join(n_plaintext_hex) + '0f' * 16, intermediary_total)
# print(new_cipher)
# cookie2decoded = decryption(new_cipher)
# print(cookie2decoded)
#
# correct = [int(plaintext_hex[i:i+2],16) for i in range(0, len(plaintext_hex), 2)]
# our = [i for i in cookie2decoded]

1
