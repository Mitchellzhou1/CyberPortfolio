nmap -sC -sV -p- 10.129.234.54 

<img width="775" height="389" alt="image" src="https://github.com/user-attachments/assets/71861cdb-3867-48c0-b554-340edea84a6d" />


j.matthew@nexus.htb

I checked the history of the .env file and saw that they removed the old DB_password: `N27xh!!2ucY04`
<img width="569" height="465" alt="image" src="https://github.com/user-attachments/assets/3a17d4c4-46c3-498c-a43d-bfe5717ac269" />


Combined the j.matthew@nexus.htb email with this password and was able to log into Krayin. Krayin version number was 2.2.0 which is vulnerable to CVE 2026-38526

https://github.com/TREXNEGRO/Security-Advisories/blob/main/CVE-2026-38526/poc.md

Followed the CVE PoC steps with Burp. The payload was saved to `http:\/\/billing.nexus.htb\/storage\/tinymce\/ec93b9b4f4657bcbb4f249fc85d950fe.php"`
<img width="1250" height="712" alt="image" src="https://github.com/user-attachments/assets/b7a836c1-204c-4142-958b-f108287876e7" />


getting RCE through webshell
<img width="840" height="339" alt="image" src="https://github.com/user-attachments/assets/41fb7cf6-4908-460f-bb94-e8671c1f672f" />
