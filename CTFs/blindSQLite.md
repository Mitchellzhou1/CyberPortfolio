# CTF Competition: BTC CTF

### CTF Name: Missing Class
**CTF Weight:** 300 points ~ 17 solves

## Writeup:

From the challenge description, it was clear that this was an SQL injection challenge since it specifically said not to use SQLMAP.

Initially, I went to the website and found that the login was indeed SQL injectable. I used an extremely basic SQL injection string into the username field; the password could be anything.

**Username**  
**Password**  
