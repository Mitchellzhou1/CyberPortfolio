# CTF Competition: picoCTF

### CTF Name: Some Assembly Required 4
**CTF Weight:** 20o points

**Link:** https://play.picoctf.org/practice/challenge/182?category=1&page=3&search=

Upon clicking on the link, I am brought to a page that asks me to enter the flag, then hit the submit button.

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/3e1302e3-c61c-4fa8-ba52-438a53822bb2)

A closer look a the submit button shows that it calls a function called `onButtonPress()`.

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/62011146-84e6-4e73-a5c9-d6b94297d5fe)

We can find the code behind this function in the file `rqe4VVml5W.js` under sources

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/12b5d2d9-4fef-4078-ba9a-bbd6d1503361)


To be honest, the CTF name is a little... misleading. You just need to reverse the javascript, there is no assembly.
Anyways, I was able to reverse the javascript:
