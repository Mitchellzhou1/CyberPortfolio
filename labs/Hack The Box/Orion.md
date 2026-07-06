# HTB Orion Writeup

<img width="865" height="236" alt="image" src="https://github.com/user-attachments/assets/a82188c5-af93-418c-93a7-0279566fde1e" />
Easy Linux box. CraftCMS RCE -> creds -> SSH -> telnetd bypass to root.

## Foothold

Site is running CraftCMS, version exposed on the login page as 5.6.16, which is vulnerable to CVE-2025-32432 (unauthenticated RCE). Used the Metasploit module for it and got a shell as `www-data`.

Ran `cat /etc/passwd` to get that the user account was `adam`:

![passwd](https://github.com/user-attachments/assets/48b012b0-93c2-4ab2-9560-fd95171b1177)

## Creds

CraftCMS `.env` file had the DB password in plaintext. No `mysql` client on the box so used PHP's mysqli to hit the DB directly and pull the admin hash from the `users` table:

![mysqli query](https://github.com/user-attachments/assets/287cb0a6-8c34-4df2-8f87-1fabda1df9aa)

Got a bcrypt hash back:
```
$2y$13$e9zuohgFZzGtbQalcn9Mz.5PJbjxobO0GMbXo8NHp3P/B42LUg0lS
```

## Cracking

```
hashcat -m 3200 -a 0 hash.txt rockyou.txt
```

![cracking](https://github.com/user-attachments/assets/88223fe1-ec97-421a-8572-a695602f393d)

Got the pass: `darkangel`

## User

Password reuse — same creds work for SSH as `adam`. Got user flag:

![user flag](https://github.com/user-attachments/assets/a50500ac-8841-422d-9934-481aa7c13eb5)

## Root

Found telnet listening on `127.0.0.1:23` only. Version was GNU inetutils telnetd 2.7, vulnerable to CVE-2026-24061 — an auth bypass. Telnetd takes the client's `USER` env var (sent via NEW_ENVIRON) and passes it straight to `login` without sanitizing it. So sending `USER="-f root"` makes it run `login -f root`, and `-f` skips the password check entirely.

```
USER="-f root" telnet -a 127.0.0.1
```

Straight to a root shell, no password needed:

![root](https://github.com/user-attachments/assets/3aa2bb31-ce62-4d39-b06e-414f36391509)

## TL;DR

1. CraftCMS unauth RCE (CVE-2025-32432) -> www-data
2. `.env` leaks DB creds -> crack admin hash -> `darkangel`
3. Password reuse -> SSH as adam -> user flag
4. telnetd auth bypass (CVE-2026-24061) via `USER=-f root` -> root
