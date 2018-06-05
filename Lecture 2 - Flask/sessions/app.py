from flask import Flask, render_template, session, request, redirect

from flask_session import Session

#session variable can be used to keep variables and values that are specific to a particular use
#give more control over sessions, store session server-side

app = Flask(__name__)


app.secret_key= 'supersecretkey'
app.config['SECRET_KEY'] = 'supersecretkey'
# SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"

Session(app)

notes = []

@app.route('/', methods=["GET", "POST"])
def index():
    if session.get("notes") is None:
        session["notes"] = []
    if request.method == "POST":
        note = request.form.get("note")
        session["notes"].append(note)
        #notes specific to my interaction

    return render_template('index.html',notes=session["notes"])
