import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("flights.csv")
    reader = csv.reader(f)
    for o, dest, dur in reader:
        db.execute("INSERT INTO flights (origin, destination, duration) VALUES (:origin, :destination, :duration)",
                    {"origin": o, "destination": dest, "duration": dur})
        print(f"Added flight from {origin} to {destination} lasting {duration} minutes.")
    db.commit() # db.execute queries will not run until db.commit() is called

if __name__ == "__main__":
    main()
