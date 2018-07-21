import os


from flask import (Flask, render_template, request, session)
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

channels = []
@app.route("/channels")
def channels_list():
    if channels:
        return render_template("channels.html", message="", channels=channels)
    return render_template("channels.html", message="No channels created yet")


@socketio.on("submit_username", namespace='/test')
def test_username(data):
    session["username"] = data["username"]
    emit(
        "username_response",
        {'username': session["username"]}
    )

@socketio.on("add_channel")
def on_add_channel(data):
    new_channel = data["channel_name"]
    channels.append(new_channel)
    emit(
        "add_channel_response",
        {"new_channel_name": new_channel}
    )

if __name__ == '__main__':
    socketio.run(app, debug=True,)