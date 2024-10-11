# CTF Competition: InfoClass CTF

### CTF Name: Padding Oracle
**CTF Weight:** EXTREME ~ only half the class solved it 😢

![Screenshot from 2024-05-25 12-04-46](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/770dabe4-6c1a-45a7-b5ae-324be140f812)



## Writeup:

The padding oracle is an attack on the padding system of the PKCS#7 padding scheme. By brute forcing each byte in the second to last block of the ciphertext, starting from the last byte, the plaintext’s last character will change. Most of the time, a change in the last value of the plaintext will result in a padding error, but there is one value which will match the PKCS#7 padding scheme in the plaintext. There is one edge case to this, which is that changing the last byte can sometimes have 2 values which is the original cipher byte and whatever byte forces it to be 0x01. We can get around this issue by skipping the original cipher byte for the last byte in the cipher block. For each byte that we brute force which matches the padding scheme, we can XOR that byte with the correct padding value to get an intermediary value. This intermediary value is extremely important because it represents the result of the ciphertext going through the encryption function with the key. The padding oracle attack allows us to figure out all the intermediary values. Since the formula for CBC encryption and decryption is Plaintext(n + 1) = Ciphertext(n) XOR Intermediary(n + 1), we are able to encrypt and decrypt cookies without the need for the original key but with just the intermediary values. 

In terms of the implementation, this attack only worked because the cookie is being signed with the same key each time. If the cookie was signed with a different key, I would get a different ciphertext each time. Since the intermediary values only map to the specific ciphertext, the intermediary values we would get would be all incorrect.


### Part 1: Encryption Attack - **Goal: Get the plaintext**

The server gives us a json cookie that is encrypted using CBC with padding scheme PKCS#7. Using the padding oracle attack, I brute forced each byte in the second to last block of the ciphertext, starting from the last byte, to get all the correct intermediary values. After finishing each cipher block and getting the corresponding intermediary value, I have to remove the block from the end of the cipher block. This is because I can only get the intermediary values by testing padding, which only appears at the end.

Slowly, you will eventually get all the intermediary blocks. Using the formula Plaintext(n + 1) = Ciphertext(n) XOR Intermediary(n + 1), we can retrieve all the plaintexts by XORing the original ciphertext with the intermediary values we just found. On the picoserver, these were the value that I retrieved (in hex): 

`
server_cookie = '5468697320697320616e204956343536c9231e442bef921941f54a268311950eb91cc2ffda59545073fe52c108c14cb7f925bccf1f402c869790a7e80614b22c2cd7fedcde70378aff83be9b78448602c714e50740c8d880c9364e031fc69c25'
`

`
intermediary_server = '2f4a1c00451b1d410c0b027376165243ac506a6607cfb07c39852354e662b734993ef0cfea69796042d362f62aed6c959056e3ae7b2d45e8b5aa87ca6075de5f49f583d1d37d3a87f28eb39675498b0f'
`

`
plaintext_server = '7b22757365726e616d65223a20226775657374222c202265787069726573223a2022323030302d30312d3037222c202269735f61646d696e223a202266616c7365227d0d0d0d0d0d0d0d0d0d0d0d0d0d'
`
![image](https://github.com/user-attachments/assets/b11ee898-1bd0-4347-a000-d10b8734c78e)


<img src="https://github.com/user-attachments/assets/b0f52dfa-843c-4cb4-a355-a5d6e0be69a1" alt="XOR value" width="400" height="auto">

	
Decoded, the plaintext value is `{"username": "guest", "expires": "2000-01-07", "is_admin": "false"}`

### Part2 Decryption Attack: **Goal: Encrypt a new json that will get me the flag.**
	
To get the flag, I must have the is_admin field set to true and also the expires field set to a future date. I decided to alter the json to be `{"username": "guest1", "expires": "2030-01-07", "is_admin": "true"}. `

Now, remember the original formula was:

`Plaintext(n + 1) = Ciphertext(n) XOR Intermediary(n + 1) `

We can rewrite this to be:

`Ciphertext(n) = Plaintext(n + 1) XOR Intermediary(n + 1)`

** It is important to know that I added an additional block to the plaintext and ciphertext because to get ciphertext(n), I need plaintext(n+1) and intermediary(n+1). But to calculate intermediary(n+1), I need an additional cipher block at the end. This cipher block can be anything, as we are only interested in the intermediary values. Rember, the intermediary(n) is the ciphertext(n) passed through the encryption function, so intermediary(n+1) is a function of ciphertext(n+1).

So my new values (with padding and hex encoded) are: 
`new_plaintext = '7b22757365726e616d65223a2022677565737431222c202265787069726573223a2022323033302d30312d3037222c202269735f61646d696e223a202274727565227d0d0d0d0d0d0d0d0d0d0d0d0d0d0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f'`


`server_cookie = '5468697320697320616e204956343536c9231e442bef921941f54a268311950eb91cc2ffda59545073fe52c108c14cb7f925bccf1f402c869790a7e80614b22c2cd7fedcde70378aff83be9b78448602c714e50740c8d880c9364e031fc69c2500000000000000000000000000000000'`


Now, with these values I can perform a similar padding oracle attack as the encryption attack. The main difference is that I am now XORing the plaintext(n) with intermediary(n) to get ciphertext(n-1). It is important to note that after getting the correct ciphertext block, I have to replace the old ciphertext block at the end with the new ciphertext block. This is, again, required because the intermediary values map to that specific ciphertext. So we have to always be sure that the intermediary values are for the correct ciphertext. Slowly, I was able to get the following results:

`new Cookie (hex): cea4c0f6991c146f4792fcec4e5b95f89ce38bf3abf25c0ec092d1c0370d22344c8e5f4296371a29216aa2df5f4d875273029f3faab424523365fcde9a4f3a22d51fb6b62f4142a56fb268ebed9875f70686b2a92920c06e25d0bcc270ec012c
IntermediaryValues: b586b585fc6e7a0e2af7ded66e79f28df990ffc289de7c2ca5eaa1a94568511676ae7d70a6042a04115b8fef686fab72516bec60cbd0493b5d47c6feb83b4857b03dcbbb224c4fa862bf65e6e09578fa0989bda6262fcf612adfb3cd7fe30e23
`
![image](https://github.com/user-attachments/assets/ccd61269-b2c2-413c-9bb1-af60e79e0ab3)


Submitting this new cookie gave me the flag.

![image](https://github.com/user-attachments/assets/8a75a58e-8c9c-413a-8986-e79b80b549bc)



this one took a while...
![image](https://github.com/user-attachments/assets/04252f5e-23b9-4d4f-bb1c-b66c10332cb3)
