import os


from flask import (Flask, render_template, request)
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


@app.route("/todo")
def todo():
    return render_template("todo.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    socketio.run(app)