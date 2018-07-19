import os
import requests
import json
from flask import (Flask, session, render_template, url_for,
                   redirect, request, jsonify)
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
            return render_template(
                url_for("register"), message="That username has already been taken!"
            )
        else:
            email = request.form["email"]
            password_hash = generate_password_hash(request.form["password"])
            db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password_hash)",
                {"username": username, "email": email, "password_hash": password_hash},
            )
            db.commit()
            session["username"] = username
            return redirect(url_for("search"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username") != None:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        stored_user_data = db.execute(
            "SELECT username, password_hash from users WHERE username= :username",
            {"username": username},
        ).fetchone()
        password_match = check_password_hash(stored_user_data.password_hash, password)

        if stored_user_data == None:
            render_template(url_for("login"), error_msg="Incorrect username")
        elif password_match == False:
            return render_template(url_for("login"), error_msg="Incorrect password")
        else:
            session["username"] = username
            return redirect(url_for("search"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username")
    return redirect(url_for("index"))


@app.route("/search")
def search():
    return render_template("book_search.html", username=session["username"])


@app.route("/results/", methods=["POST"])
def results():
    search = request.form["search"]
    if search == "":
        return redirect(url_for("books"))
    try:
        year = int(search)
        results = db.execute("SELECT * FROM books WHERE year=:year", {"year": year})
    except:
        results = db.execute(
            "SELECT * from books WHERE isbn LIKE :search: OR author LIKE :search: OR title LIKE :search:",
            {"search": search},
        ).fetchall()

    if results:
        return render_template("book_list.html", book_list=results)
    return "No books in the database match your results"


@app.route("/books")
def books():
    if session["username"]:
        book_list = db.execute(
            "SELECT isbn, title, author, year, id  FROM books"
        ).fetchall()
        return render_template("book_list.html", book_list=book_list)


@app.route("/results/<int:book_id>")
def book_detail(book_id):
    book = db.execute(
        "SELECT isbn, title, author, year, id FROM books WHERE id=:book_id",
        {"book_id": book_id},
    ).fetchone()

    user_review = db.execute(
        "SELECT review FROM user_reviews WHERE username = :username AND book_isbn = :book_isbn",
        {"username": session["username"], "book_isbn": book.isbn}
    ).fetchone()


    res = requests.get(
        "https://www.goodreads.com/book/review_counts.json",
        params={"key": "1YUBwhz7YgYKG2WUX6O07w", "isbns": book.isbn},
    )
    average_rating = res.json()["books"][0]["average_rating"]
    work_ratings_count = res.json()["books"][0]["work_ratings_count"]

    return render_template(
        "book_detail.html",
        book=book,
        average_rating=average_rating,
        work_ratings_count=work_ratings_count,
        user_review=user_review,
    )

@app.route('/submit_review/<string:book_isbn>', methods=["POST"])
def submit_review(book_isbn):
    user_review = db.execute(
        "SELECT review FROM user_reviews WHERE username = :username AND book_isbn = :book_isbn",
        {"username": session["username"], "book_isbn": book_isbn}
    ).fetchone()

    if user_review:
        return render_template('error.html', message="You have already reviewed this book")
    else:
        username = session['username']
        review = request.form.get("review")
        rating = request.form.get("rating")

        db.execute(
            "INSERT INTO user_reviews (username, book_isbn, review, rating) VALUES (:username, :book_isbn, :review, :rating)",
            {"username": username,
             "book_isbn": book_isbn,
             "review": review,
             "rating": rating}
        )
        db.commit()

        return render_template("success.html", message="You have successfully submitted your review")

@app.route('/my_reviews')
def my_reviews():
    reviews = db.execute(
        "SELECT title, author, review FROM books JOIN user_reviews ON books.isbn = user_reviews.book_isbn"
    ).fetchall()
    return render_template("my_reviews.html", reviews=reviews)

@app.route('/api/<string:isbn>', methods=["GET"])
def api(isbn):

    book = db.execute(
        "SELECT title, author, year FROM books WHERE isbn = :isbn",
        {"isbn": isbn}        
    ).fetchone()

    if book:
        response = requests.get(
            "https://www.goodreads.com/book/review_counts.json",
            params={"key": "1YUBwhz7YgYKG2WUX6O07w", "isbns": isbn},
        ).json()["books"][0]
        
        result = {
            'title': book.title,
            'author': book.author,
            'year': int(book.year),
            'isbn': isbn,
            'review_count': response["reviews_count"],
            'average_score': response["average_rating"]
        }
        
        return jsonify(result)
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

