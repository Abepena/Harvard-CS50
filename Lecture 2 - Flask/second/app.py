from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    headline = "Hello!"
    return render_template("index.html", headline=headline)
    """
    Flask only looks immediately inside a directory called templates in the same directory as the app.py
    """

@app.route('/bye')
def bye():
    headline = 'Goodbye!'
    return render_template("index.html", headline=headline)
