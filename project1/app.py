import os
import requests
from flask import (Flask, session, render_template,
                     url_for, redirect, request, flash)
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# session["username"] = None
# session["logged_in"] = False

@app.route("/", methods=["GET"])
def index():
    if session.get("username") == None:
        return render_template("welcome.html")
    return redirect(url_for('search'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        if (
            db.execute(
                "SELECT * from users WHERE username= :username", {"username": username}
            ).rowcount
            > 0
        ):
            return render_template(url_for("register"), message="That username has already been taken!")
        else:
            email = request.form["email"]
            password_hash = generate_password_hash(request.form["password"])
            db.execute(
                "INSERT INTO users (username, email, password_hash)\
                VALUES (:username, :email, :password_hash)",
                {"username": username, "email": email, "password_hash": password_hash},
            )
            db.commit()
            session["username"] = username
            return redirect(url_for("search"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username") != None:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        stored_user_data = db.execute(
            "SELECT username, password_hash from users WHERE username= :username",
            {"username": username}
        ).fetchone()
        password_match = check_password_hash(stored_user_data.password_hash, password)

        if stored_user_data == None:
            render_template(url_for("login"), error_msg="Incorrect username")
        elif password_match == False:
            return render_template(url_for("login"), error_msg="Incorrect password")
        else:
            session["username"] = username
            return redirect(url_for('search'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username')
    return redirect(url_for("index"))

@app.route("/books")
def books():
    if session["username"]:
        book_list = db.execute("SELECT isbn, title, author, year FROM books").fetchall()
        return render_template("book_list.html", book_list=book_list)

@app.route('/search')
def search():
    return render_template('book_search.html')

@app.route('/results/', methods=["POST"])
def results():
    search = request.form["search"]
    try:
        year = int(search)
        results = db.execute(
            "SELECT * FROM books WHERE year=:year",
            {"year": year}
        )
    except:
        results = db.execute(
            "SELECT * from books WHERE\
            isbn LIKE :search OR author LIKE :search OR title LIKE :search",
            {"search":"%" + search + "%"}
        ).fetchall()
    
    if results:
        return render_template('book_list.html', book_list=results)
    return "No books in the database match your results"

if __name__ == "__main__":
    app.run(debug=True)
