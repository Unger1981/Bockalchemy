from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import  Authors, Books, add_to_db, get_data, get_cover_author, db
import os

db_path = os.path.abspath(os.path.join("data", "library.sqlite"))


app = Flask(__name__) 


app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/", methods = ['GET'])
def home():
     try:
          data = get_data()
          books, authors = data  
     except Exception as e:
          return jsonify(message= f"Couldnt receive data from database.Error {e}" ), 500 
     return render_template('home.html', books=books, authors=authors), 200
    



@app.route("/add_author", methods=['GET', 'POST'])
def add_author(): 
     if request.method == "GET":
          try:
               return render_template('add_author.html'), 200
          except Exception as e:
               print(f"Error while trying to render the template. Error {e}"), 500    
     elif request.method == "POST":
          author = request.form.get('author')
          birthday = request.form.get('birthdate')
          date_of_death = request.form.get('date_of_death')
          new_author = Authors(name=author, birthdate=birthday, date_of_death=date_of_death)
          try:
               add_to_db(new_author)
          except Exception as e:
               return jsonify(message=(f"Couldnt store to database. Error {e}")), 500    
               
          return redirect(url_for('home'), code=302)
         

@app.route("/add_book", methods = ['GET', 'POST'])
def add_book():
     if request.method == "GET":
          print("Generated Template")
          return render_template('add_book.html')
          
     elif request.method == "POST":
          title = request.form.get('title')
          isbn = request.form.get('isbn')
          book_cover,author = get_cover_author(isbn)
          publication_year = request.form.get('publication_year')
          new_book = Books(title = title , author = author , isbn = isbn , book_cover = book_cover , publication_year=publication_year)
          print(new_book)
          try:
               add_to_db(new_book)
          except Exception as e:
               return jsonify(message=(f"Couldnt store to database. Error {e}")), 500  
          return redirect(url_for('home'), code=302)



if __name__ == "__main__":
    host = "127.0.0.1"  # Use "0.0.0.0" to allow external access, or "127.0.0.1" for local only
    port = 5000  # Change this if needed
    print(f"Running on http://{host}:{port}/")  # Display URL in console
    app.run(host=host, port=port, debug=True)  # Start Flask server
