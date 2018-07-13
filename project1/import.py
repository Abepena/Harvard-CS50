import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))

def main():
    with open("books.csv", 'r', newline='') as f:
        has_header = csv.Sniffer().has_header(f.read()) #Looks for header
        f.seek(0) # Rewinds to the beginning of the file
        reader = csv.reader(f)
        if has_header:
            next(reader) # Skips header if found
            for isbn, title, author, year in reader:
                db.execute("INSERT INTO books(isbn, title, author, year)\
                             VALUES (:isbn, :title, :author, :year)",
                             {"isbn": isbn, "title": title,
                              "author": author, "year": year})
                print(f"Added {title} by {author}, ISBN: {isbn}")
            db.commit()

if __name__ == "__main__":
    main()