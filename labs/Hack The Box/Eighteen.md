# Hack The Box: Eighteen

### Challenge Name: Eighteen
**Difficulty:** Easy

<img width="319" height="131" alt="Screenshot from 2025-11-18 18-02-34" src="https://github.com/user-attachments/assets/932ff127-487e-4de2-bf66-e715caf2e2e9" />


## Writeup:

I was given the creds `kevin / iNa2we6haRj2gaw!`

To start, I ran nmap on the ip address to see what ports were exposed:

`nmap -sV 10.10.11.95`

<img width="785" height="264" alt="image" src="https://github.com/user-attachments/assets/2f1e20bb-ca27-4450-bd02-a32bdae9a1cd" />

So there is an Webserver, SQL server, and Windows Remote Desktop Server.

I was able to log into the SQL server via the provided credentials: 
`impacket-mssqlclient kevin:'iNa2we6haRj2gaw!'@10.10.11.95`

After logging in, I checked sys.sql_logins and saw that there were 3 accounts, I was able to login as `appdev` with no issues through `EXECUTE AS LOGIN = 'appdev'`

<img width="603" height="143" alt="image" src="https://github.com/user-attachments/assets/3cba9337-4ab0-46b7-a2ce-c0f8f1698365" />

The appdev account has the permission to view any table! This means I can view the `financial_planner` table which I previously could not with just `kevin's` creds.

<img width="1538" height="152" alt="image" src="https://github.com/user-attachments/assets/5f61abb3-43fc-4484-a36f-889bc5ddc542" />

Now I was interested in the admin account so I loaded up hashcat and cracked it:
**note the hash given in the db needs to be converted before it can be used by hashcat.**

so now I have the password= `iloveyou1` for admin.
```
sha256:600000:QU10enRlUUlHN3lBYlpJYQ==:BnOtkKC0r7GdZiM28Pzjqe3Qt7GRk3F74ozk1myIcTM=:iloveyou1
```

<img width="852" height="344" alt="image" src="https://github.com/user-attachments/assets/bf161ae2-f2c6-4aa6-948b-ac9f825d344f" />

These credentials only worked on the web app, I was not able to use `admin:iloveyou1` anywhere else like on the WinRM. This was a bit confusing so I did more recon and tried an RID brute-force through SMB instead.


<img width="1059" height="689" alt="image" src="https://github.com/user-attachments/assets/81c21fac-6b6b-4fc3-8873-cd9887eee420" />

with this infomration I build a `user.txt` and tested if the `iloveyou1` password was reused... and it was by `adam.scott`

<img width="952" height="570" alt="image" src="https://github.com/user-attachments/assets/ddfac9c3-ea88-462d-8543-05aa8cb580ec" />


### Escalation to root
couldn't excalate unfortunatley :(

I did some research into Windows Server 2025 Build 26100 and found this article `https://www.covertswarm.com/post/bad-successor-technical-deep-dive` on using badsuccessor to privilege escalate.

The article states that in order to preform this, I need **one** of the following three permisions to execute this attack:

- `Access to an existing dMSA account`
- `Appropriate privileges such as CreateChild, GenericAll, WriteDACL, or WriteOwner on an Organizational Unit (OU) in the domain`
- `Write permissions on existing dMSA objects`

After checking my permissions, 

`whoami /all`
<img width="960" height="852" alt="image" src="https://github.com/user-attachments/assets/0632932b-6dd9-43d0-a11d-cfcd5e4432bd" />


`Get-DomainObjectAcl "OU=Staff,DC=eighteen,DC=htb" -ResolveGUIDs | Where-Object {$_.SecurityIdentifier -eq "S-1-5-21-1152179935-589108180-1989892463-1604"}`
<img width="948" height="320" alt="image" src="https://github.com/user-attachments/assets/42bd7e41-1ef4-4c9d-ad61-27f2859d03b2" />


Sp, the `EIGHTEEN\IT` group has CreateChild rights on OU=Staff

Since adam scott is a member of EIGHTEEN\IT.

That means I can create objects in OU=Staff which is exactly the prerequisite the article requires.

But no matter that I tried, I kept getting hit with missing permissions. : (


<img width="952" height="762" alt="image" src="https://github.com/user-attachments/assets/06a7cb40-9a61-4b45-9088-eea26ef9a291" />





