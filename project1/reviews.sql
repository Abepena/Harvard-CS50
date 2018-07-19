CREATE TABLE user_reviews(
    id SERIAL PRIMARY KEY,
    username VARCHAR REFERENCES users(username),
    book_isbn VARCHAR REFERENCES books(isbn),
    review VARCHAR NOT NULL
);