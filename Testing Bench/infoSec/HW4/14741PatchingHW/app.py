from flask import Flask
from flask.templating import render_template

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello_world():
    return 'Hello World'

app.run("127.0.0.1", port=14741, debug=True)