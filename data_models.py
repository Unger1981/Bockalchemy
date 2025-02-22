from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os, requests, json

# Define database path and engine


db_path = os.path.join("data", "library.sqlite")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
db = SQLAlchemy()

class Authors(Base):
    """
    Represents an author in the library system.
    """
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    birthdate = Column(String)
    date_of_death = Column(String)
    books = relationship("Books", back_populates="author")

    def __repr__(self):
        return f"Author(id={self.id}, name={self.name})"

class Books(Base):
    """
    Represents a book in the library system.
    """
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String)
    title = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship("Authors", back_populates="books")
    book_cover = Column(String)
    publication_year = Column(Integer)

    def __repr__(self):
        return f"Book(id={self.id}, title={self.title})"

# Initialize database tables
Base.metadata.create_all(engine)

def add_to_db(db_object):
    """
    Adds an object to the database and commit.
    """
    try:
        db.session.add(db_object)
        db.session.commit()
        shutdown_session()
    except Exception as e:
        return jsonify(message=f"Unable to store object into Database. Error: {e}"), 500

def get_data():
    """
    Retrieves all books and authors from the database.
    """
    try:
        books = session.query(Books).all()
        authors = session.query(Authors).all()
        shutdown_session()
        return books, authors
    except Exception as e:
        return jsonify(message=f"Requested data not found. Error: {e}"), 500

def get_cover(isbn):
    """
    Fetches the book cover image URL using the Google Books API.
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        response = requests.get(url)
        data = response.json()
        cover_url = data["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
        return cover_url
    except Exception as e:
        print(f"Could not get book cover from API. Error: {e}")
        return "no cover"

def shutdown_session(exception=None):
    db.session.remove()        

