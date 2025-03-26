import os
import sqlite3
import pymongo
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

#  SQLite Database
DATABASE = os.path.join(os.getcwd(), 'book-reviews-app/db/books.db')

#  Ensure the database directory exists
if not os.path.exists(os.path.dirname(DATABASE)):
    os.makedirs(os.path.dirname(DATABASE))

#  Initialize SQLite Database
def init_sqlite_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        publication_year INTEGER
    )''')
    conn.commit()
    conn.close()

# Call this function before using the database
init_sqlite_db()

#  MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['book_database']
reviews_collection = db['reviews']

#  Fetch All Books
@app.route('/api/books', methods=['GET'])
def get_all_books():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, publication_year FROM Books")
    books = cursor.fetchall()
    conn.close()

    book_list = [{'book_id': book[0], 'title': book[1], 'publication_year': book[2]} for book in books]
    return jsonify({'books': book_list})

#  Add a New Book
@app.route('/api/add_book', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data.get('title')
    publication_year = data.get('publication_year')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Books (title, publication_year) VALUES (?, ?)", (title, publication_year))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Book added successfully'})

#  Add a Review (Stored in MongoDB)
@app.route('/api/add_review', methods=['POST'])
def add_review():
    data = request.get_json()
    book_id = data.get('book_id')
    user = data.get('user')
    rating = data.get('rating')
    comment = data.get('comment')

    review = {'book_id': book_id, 'user': user, 'rating': rating, 'comment': comment}
    reviews_collection.insert_one(review)

    return jsonify({'message': 'Review added successfully'})

#  Fetch All Reviews with Book Titles
@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    reviews = list(reviews_collection.find({}, {'_id': 0}))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for review in reviews:
        cursor.execute("SELECT title FROM Books WHERE id = ?", (review['book_id'],))
        book_title = cursor.fetchone()
        review['book_title'] = book_title[0] if book_title else "Unknown Book"

    conn.close()

    return jsonify({'reviews': reviews})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
