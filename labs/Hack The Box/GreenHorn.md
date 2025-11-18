# Hack The Box: Green Horn

### Challenge Name: Green Horn
**Difficulty:** Easy

![image](https://github.com/user-attachments/assets/9d579f42-4378-4cc0-8183-aa3ae39557d3)


## Writeup:

To start, I ran nmap on the ip address to see what ports were exposed:

`nmap -sV 10.10.11.25`

![image](https://github.com/user-attachments/assets/6535f137-356a-47d1-882c-7194a67e62f5)


Although initially port 3000 showed up as an unrecongized service, I went to http://10.10.11.25:3000/ in my browser and saw that it was a Gitea service.

![image](https://github.com/user-attachments/assets/b8c04bca-69dc-4ea6-bee1-6539757e3a19)

So here are the final results:
| **Port**       | **Service** |
|--------------------|--------------|
| `22`     | `ssh`          |
| `80`     | `Webserver - Pluck 4.7.18`          |
| `3000`     | `Webserver - Gitea Service`          |

In the Gitea website, there was one opensource repository called GreenHorn. This repository had the full source code for the Pluck website!!
While browsing the source code, I came across the login.php and saw that it was comparing my input with a the variable `$ww`. 

![image](https://github.com/user-attachments/assets/f0d442cb-f67f-4b75-a0fe-c3deb80d59eb)

A search through the repository found that the `$ww` variable was stored in `/data/settings/pass.php`

![image](https://github.com/user-attachments/assets/8d1d8789-101b-4db4-a195-d49a4dcfeb9a)


To crack this hash, I used hashcat and got the admin password of `iloveyou1`

`hashcat -m 1800 -a 0 hash.txt rockyou.txt`

![image](https://github.com/user-attachments/assets/b24bf56e-e21d-438d-aebc-9dacb38ebb15)


I used this password in [http://10.10.11.25:80/login.php](http://greenhorn.htb/login.php) and was able to get into the admin panel. I found a RCE vulnerability in Pluck 4.7.18. I used a php reverse shell from 
`https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php` and installed a zipped version of it into the modules of Pluck.
![image](https://github.com/user-attachments/assets/e4eeec92-66e6-4130-9ab8-00872eefc04f)


After this, I was able to get a reverse shell spawned!!

![image](https://github.com/user-attachments/assets/998aa5f1-61bd-4602-bbf4-04f9cd089486)


After logging in as Junior (using password `iloveyou1`) I was able to red the user.txt file which contained the first flag.
![image](https://github.com/user-attachments/assets/b95954c1-d3da-4e05-b60b-556ba2acbe85)


Now to get the root flag, I exported out the `Using OpenVAS.pdf` file through netcat back to my local machine. Upon opening the PDF I got a blurred password image.

![image](https://github.com/user-attachments/assets/72840817-8c23-401c-b7b2-970d0732a1a0)

I used an depixelator tool with the commands:

```
git clone https://github.com/spipm/Depix.git
cd Depix
python3 depix.py -p ~/Pictures/pix.png -s ./images/searchimages/debruinseq_notepad_Windows10_closeAndSpaced.png -o output.png
```

![image](https://github.com/user-attachments/assets/f64a19c5-1681-4276-b26c-5e6d39265ae1)


I entered this into the root password (`sidefromsidetheothersidesidefromsidetheotherside`) and was able to get the system flag.

![image](https://github.com/user-attachments/assets/cc9d50e4-8dfc-489d-aa7a-1120370c734e)


