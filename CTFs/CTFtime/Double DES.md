# CTF Competition: picoCTF

### CTF Name: Double DES
**CTF Weight:** 12o points

**Link:** https://play.picoctf.org/practice/challenge/140?page=1&search=des

Double DES (Data Encryption Standard) refers to using the DES algorithm twice consecutively with two different keys for encrypting data. The process involves encrypting the plaintext first with one DES key, and then encrypting the output again with a different DES key.

As you can see from the picture below, this is a symmetric encryption algorithm. With key1 and key2, I will be able to decrypt the ciphertext.


<img src="https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/7e667b38-fad9-4b0c-aa0a-6c1f371c666a" style="width: 40vw;">


## My Challenge:


![Screenshot from 2024-05-26 19-15-34](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/7ded6229-e685-4e1e-8ac5-5d4dc1df2c10)

In this challenge, I am asked to netcat into their server and told to decode the Double DES Encrypted text. They provided the code that they used to encrypt the flag. One other attribute of the challenge that I was able to take advantage of was the fact that in the netcat connection, they let the user encrypt their own messages!

So upon examining the code, I found the following:
1) The key space is only 6 digits + 2 spaces for padding, so total is 8. So realistically I just need to brute force 10^6 digits which is reasonable.

![Screenshot from 2024-05-26 19-18-34](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/977fc22a-5b31-45ef-8c9d-3c79ee5e694b)

 
2) They reuse the same keys for encrypting the user’s text!!! Because DES is a symmetric encryption, I just need to figure out the keys and use them to decode the flag!
![Screenshot from 2024-05-26 19-20-17](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/9c7b1b03-60e6-4705-9a2d-d509ddc4d620)

I did some research into vulnerabilities of Double DES and found an attack called Meet-in-the-Middle attack. The idea of this attack is that I first brute force all keys in the keyspace and just those keys to encrypt the plain text -> let's call this E1. Then I take the second key and use it to decrypt the ciphertext -> let's call the result of this decryption E2. If I find a match where E1 == E2, then I know that I have found the two pairs of keys used to encrypt the flag!!! The attack depends on being able to control the initial plaintext and knowing what the ciphertext at the end of the double encryption will be.


![Screenshot from 2024-05-26 19-20-27](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/6f59b158-af9f-4b7f-a8df-5c61d856b8ee)

   

In this challenge, I exposed the fact that they allowed me to encrypt my own messages and see the ciphertext at the end. Sooo, this is what I did:

![Screenshot from 2024-05-26 19-20-39](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/a16d95e0-493d-4c7a-850d-995b70cbef0d)




### What I know:

1) Ciphertext Flag: 3494708d8f9c6563da734dd7547424b044e767b2ed05ec07b63c8804166fa3b0fa8af43825da9529
2) Custom plain text = 11111111
3) Customer cipher text = 4ac0735cde4c60d6

### Need to know:

1) Key 1: will figure this out with brute force
2) Key 2: will figure this out with brute force
3) Plain text: will figure out by decoding the Ciphertext Flag with the two keys!!!




### Script:

```python
from Crypto.Cipher import DES
import binascii

def pad(msg):
    block_len = 8
    over = len(msg) % block_len
    pad = block_len - over
    return (msg + " " * pad).encode()

def encrypt(KEY, msg):
    cipher1 = DES.new(KEY, DES.MODE_ECB)
    nc_msg = cipher1.encrypt(msg)
    return enc_msg

def decrypt(KEY, ciphertext):
    ciphertext = binascii.unhexlify(ciphertext)
    cipher2 = DES.new(KEY, DES.MODE_ECB)
    enc_msg = cipher2.decrypt(ciphertext)
    return enc_msg

def decode(key1, key2, cipher_text):
    ciphertext = binascii.unhexlify(cipher_text)
    cipher2 = DES.new(key2, DES.MODE_ECB)
    enc_msg = cipher2.decrypt(ciphertext)
    cipher1 = DES.new(key1, DES.MODE_ECB)
    plaintext_padded = cipher1.decrypt(enc_msg)
    plaintext = plaintext_padded.rstrip(b'\0')
    return plaintext.decode().strip()

my_text = pad(binascii.unhexlify("11111111").decode())
my_text_encrypt = binascii.unhexlify("4ac0735cde4c60d6")
ciphertext = "3494708d8f9c6563da734dd7547424b044e767b2ed05ec07b63c8804166fa3b0fa8af43825da9529"

encryption_results = {}
FINAL_key1 = None
FINAL_key2 = None

print("Running first key")
for key in range(999999):
    key = (f"{key:06}" + ' ').encode()
    cipher = DES.new(key, DES.MODE_ECB)
    encrypted_msg = cipher.encrypt(my_text)
    encryption_results[encrypted_msg] = key

print("Finished Key 1 Encryption Table")

print("Running second Key")
for key in range(999999):
    key = (f"{key:06}" + ' ').encode()
    cipher = DES.new(key, DES.MODE_ECB)
    encrypted_msg = cipher.decrypt(my_text_encrypt)
    if encrypted_msg in encryption_results.keys():
        print("Found the keys!!!")
        FINAL_key1 = encryption_results[encrypted_msg]
        FINAL_key2 = key
        break

print("Key 1 =", FINAL_key1)
print("Key 2 =", FINAL_key2)

print("Flag is:")
print(decode(FINAL_key1, FINAL_key2, ciphertext))
```
The Results:

![Screenshot from 2024-05-26 19-23-47](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/c936d757-4acd-4637-bf08-bbfd7a42fe3b)


‭So the final flag is:‬‭ e21cf83f64e53a743e685e55852feaf2‬ 😎
