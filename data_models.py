from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String ,create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os, requests

db_path = os.path.join( "data", "library.sqlite")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base() 
db = SQLAlchemy()


class Authors(Base): 
    __tablename__ = 'authors' 
 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String) 
    birthdate = Column(String) 
    date_of_death = Column(String) 
 
    def __repr__(self): 
        return f"Author(id={self.id}, name={self.name})"

class Books(Base): 
    __tablename__ = 'books' 
 
    id = Column(Integer, primary_key=True, autoincrement=True) 
    isbn = Column(String) 
    title = Column(String) 
    publication_year = Column(Integer) 
    book_cover = Column(String)
 
    def __repr__(self): 
        return f"Book(id={self.id}, title={self.title})"

# creating the tables
Base.metadata.create_all(engine)

def add_to_db(db_object):
    try:
        db.session.add(db_object)
        db.session.commit() 
    except Exception as e:
        return jsonify(message=f"Unable to store object into Database. Error: {e}"), 500


from flask import jsonify

def get_data():
    try:
        books = session.query(Books).all()  
        authors = session.query(Authors).all()
        return books, authors
    except Exception as e:
        return jsonify(message=f"Requested data not found. Error: {str(e)}"), 500


def get_book_cover(isbn):
    url=f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    data = response.json()
    cover_url = data.get('smallThumbnail', 'no return')
    print(cover_url)
    return cover_url


