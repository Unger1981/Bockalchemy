from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import Authors, Books, add_to_db, get_data, get_cover, db, shutdown_session
import os

db_path = os.path.abspath(os.path.join("data", "library.sqlite"))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/", methods=['GET'])
def home():
    """
    Renders the homepage with a list of books and authors.
    Supports search and sorting functionality.
    
    Query Parameters:
        search (str): Filters books by title or author name.
        sort_by (str): Sorts books by "title" (default) or "author".
    
    Returns:
        Renders 'home.html' template with filtered and sorted book data.
    """
    try:
        data = get_data()
        books, authors = data

        search_query = request.args.get("search", "")
        sort_by = request.args.get("sort_by", "title")

        if search_query:
            books = [book for book in books if search_query.lower() in book.title.lower() or (book.author and search_query.lower() in book.author.name.lower())]

        if sort_by == "author":
            books = sorted(books, key=lambda x: x.author.name if x.author else "Unknown")
        else:
            books = sorted(books, key=lambda x: x.title)

    except Exception as e:
        return jsonify(message=f"Could not retrieve data from database. Error: {e}"), 500

    return render_template('home.html', books=books, authors=authors, search_query=search_query, sort_by=sort_by), 200

@app.route("/add_author", methods=['GET', 'POST'])
def add_author():
    """
    Handles adding a new author to the database.
    
    GET: Renders the author addition form.
    POST: Processes form data and adds a new author.
    
    Returns:
        Redirects to the homepage upon successful addition.
    """
    if request.method == "GET":
        try:
            return render_template('add_author.html'), 200
        except Exception as e:
            return jsonify(message=f"Error rendering template. Error: {e}"), 500    
    elif request.method == "POST":
        author = request.form.get('author')
        birthday = request.form.get('birthdate')
        date_of_death = request.form.get('date_of_death')
        new_author = Authors(name=author, birthdate=birthday, date_of_death=date_of_death)
        try:
            add_to_db(new_author)
        except Exception as e:
            return jsonify(message=f"Could not store to database. Error: {e}"), 500    
        return redirect(url_for('home'), code=302)

@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    """
    Handles adding a new book to the library.
    
    GET: Renders the book addition form.
    POST: Processes form data and adds a new book to the database.
    
    Returns:
        Redirects to the homepage upon successful addition.
    """
    if request.method == "GET":
        try:
            data = get_data()
            books, authors = data  
        except Exception as e:
            return jsonify(message=f"Could not receive data from database. Error: {e}"), 500 
        return render_template('add_book.html', books=books, authors=authors), 200
    elif request.method == "POST":
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        author_id = request.form.get('author')
        book_cover = get_cover(isbn)
        publication_year = request.form.get('publication_year')
        new_book = Books(title=title, author_id=author_id, isbn=isbn, book_cover=book_cover, publication_year=publication_year)
        try:
            add_to_db(new_book)
        except Exception as e:
            return jsonify(message=f"Could not store to database. Error: {e}"), 500  
        return redirect(url_for('home'), code=302)

@app.route("/book/<int:book_id>/delete", methods=['GET', 'POST'])
def delete_book(book_id):    
    book_to_delete = db.session.get(Books, book_id)
    if book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()
    data = get_data()
    books, authors = data
    book_count = 0
    for book in books:
        if book_to_delete.author_id == book.author_id:
            book_count+=1
    if book_count == 0:
        print("Author deletion")
        author_to_delete = db.session.query(Authors).get(book_to_delete.author_id)
        db.session.delete(author_to_delete)
        db.session.commit()
    shutdown_session()

    return redirect('/')   

if __name__ == "__main__":
    """
    Starts the Flask application on the specified host and port.
    """
    host = "127.0.0.1"  # Use "0.0.0.0" for external access, or "127.0.0.1" for local
    port = 5000  # Change if needed
    print(f"Running on http://{host}:{port}/")  
    app.run(host=host, port=port, debug=True)
