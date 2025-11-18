# Hack The Box: Cap 

### Challenge Name: Cap
**Difficulty:** Easy

![image](https://github.com/user-attachments/assets/11666352-8485-4d72-8d69-607469631aeb)



## Writeup:

To start, I ran nmap on the ip address to see what ports were exposed:

`sudo nmap --script=default,vuln 10.10.10.245`

![image](https://github.com/user-attachments/assets/2b327624-8ca8-4318-a346-3a528fdb3c37)


After going to "Security Snapshot" section from the dashboard, I saw it took me to the url 

`http://10.10.10.245/data/8`. 

Specifically, I see that in the url there is the number 8 at the end. I tried some other values and saw that the value 0 allowed me to download an interesting PCAP file.
Upon going through this pcap file, I found an FTP username and password.

![image](https://github.com/user-attachments/assets/8d4515ff-ae9b-4674-b2ee-b51b4eeb096c)

```
User: nathan
Pass: Buck3tH4TF0RM3!
```

Using these credentials I was able to log into the FTP server and exfiltrate the user.txt file (`71d2dee1add448384198c4d664f5e27d`)

![image](https://github.com/user-attachments/assets/c18f10ce-8c85-4846-bb78-abf54005c9f9)

Funny enough, in this user's home directory was LinPEAS, which is used for privilege escalation. Upon running the script, I found an interesting CVE: CVE-2021-4034: https://www.qualys.com/2022/01/25/cve-2021-4034/pwnkit.txt

![image](https://github.com/user-attachments/assets/6999d808-e820-4455-ba54-294d6435a267)

After running the exploit code, I was able to get root. I found the root flag under /root/root.txt

![image](https://github.com/user-attachments/assets/d90cfd82-52dc-4e33-a205-5e145da3012c)
![image](https://github.com/user-attachments/assets/a0ab3fd4-6ced-48b8-b752-4dcc2c8d5565)
