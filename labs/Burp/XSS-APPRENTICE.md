# Burp Suite XSS labs (APPRENTICE)

**Link:** [Burp Suite XSS labs](https://portswigger.net/web-security/all-labs#cross-site-scripting)

Here are all my solutions to the Burp Suite XSS labs (APPRENTICE) level. 

&nbsp;


&nbsp;

## Lab 1: lab-html-context-nothing-encoded
The search box is vulnerable to XSS (reflected). 
Entering `<script>alert(1)</script>` into the search will execute the reflected XSS.
![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/f98a6d66-0e5e-4e1a-bf44-f1fe7853e410)

&nbsp;


&nbsp;

## Lab 2: Stored XSS into HTML context with nothing encoded
The comment box is vulnerable to XSS (stored).
Entering `<script>alert(1)</script>` into the comment box will execute the reflected XSS.
The rest of the input field do not matter.
![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/a58a2ccc-00b4-47ef-a4a7-d351708999c2)

&nbsp;


&nbsp;

## Lab 3: DOM XSS in document.write sink using source location.search
The title and description of the lab so that the XSS is in the document.write in the search box.
To see the function, you need to initially input some data into the search box. Afterward, you see the function:
![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/0addf59a-f1e8-46a3-8040-5299184b073a)

From the code, they are concatenating our input into the image tag. So if we close the tag and the src attribute with a `">` we can
escape the the img tag and create out payload. So the final exploit was: `"><script>alert(1)</script>`

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/4fdd3326-62a1-4347-8e89-0f41ddb886fb)

&nbsp;


&nbsp;

## Lab 4: DOM XSS in innerHTML sink using source location.search
Similar to the other labs before this, we need to exploit the **search** textbox to execute XSS.
![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/f982cb46-1207-4ccb-a7d6-d6779d56f178)

From the source code, it seems like that it is getting the search input and setting that directly to the `<span id="sendMessage" >` in the DOM.

Initially, I tried just the payload `<script> alert(1) </script>` and saw that it got injected into the DOM, but the pop up did not appear ☹️.

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/7ed119f7-5411-4cb3-88c9-1a6d2fbb6e33)

This is beacuse the `innerHTML` sink doesn't accept script elements on any modern browser, nor will svg onload events fire. This means we will need to use alternative elements like `img` or `iframe`. Event handlers such as `onload` and `onerror` can be used in conjunction with these elements. 

So the final exploit was: `<img src="x" onerror=alert(1)>`

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/823e5027-d08a-4314-ab07-be6cdc67ee86)

&nbsp;


&nbsp;
