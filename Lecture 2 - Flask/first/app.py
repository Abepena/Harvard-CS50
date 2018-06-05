from flask import Flask

#creates a flask variable called app that goes by the name of the file
app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/abe")
def abe():
    return "Hello Abe!"

@app.route("/<string:name>")
def hello(name):
    name = name.capitalize()
    return f"Hello, {name}!"
