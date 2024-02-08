from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Retrieve MongoDB URI from environment variable or use default
mongo_uri = os.getenv("MONGO_URI", "mongodb://mominmongo:Aisha1234@mongodb:27017/BOOKSTORE")

# Exit if MongoDB URI is not provided
if not mongo_uri:
    logging.error("MONGO_URI environment variable is not set.")
    exit(1)

# Establish MongoDB client connection
client = MongoClient(mongo_uri)
db = client['BOOKSTORE']

# Function to validate book data in request
def validate_book_data(book_data):
    if 'title' not in book_data or 'author' not in book_data:
        abort(400, description="Missing title or author")

@app.route('/book/<string:title>', methods=['GET'])
@app.route('/book', methods=['GET'])
def get_book(title=None):
    if title:
        book = db.books.find_one({'title': title})
        if book:
            return jsonify(book), 200
        else:
            return jsonify({'error': 'Book not found'}), 404
    else:
        books = db.books.find({}, {'title': 1, '_id': 0})
        book_list = list(books)
        return jsonify(book_list)

# Route to search for books based on query parameters
@app.route('/books/search', methods=['GET'])
def search_books():
    query = request.args
    books = db.books.find(query)
    return jsonify([book for book in books])

# Route to get books with pagination
@app.route('/books', methods=['GET'])
def get_books():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    books = db.books.find({}).skip((page - 1) * per_page).limit(per_page)
    return jsonify([book for book in books])

# Route to update a book by title
@app.route('/book/<string:title>', methods=['PUT', 'GET'])
def book(title):
    if request.method == 'GET':
        book = db.books.find_one({'title': title})
        if book:
            return jsonify(book)
        else:
            return jsonify({'error': 'Book not found'}), 404
    elif request.method == 'PUT':
        update_data = request.json
        result = db.books.update_one({'title': title}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({'error': 'Book not found'}), 404
        else:
            return jsonify({'message': 'Book updated'}), 200

# Route to delete a book by title
@app.route('/book/<string:title>', methods=['DELETE'])
def delete_book(title):
    result = db.books.delete_one({'title': title})
    if result.deleted_count == 0:
        return jsonify({'error': 'Book not found'}), 404
    else:
        return jsonify({'message': 'Book deleted'}), 200

# Route to test MongoDB connection
@app.route('/test_db')
def test_db():
    try:
        db.test_collection.find_one()
        return "Connected to MongoDB successfully!"
    except Exception as e:
        return f"Failed to connect to MongoDB: {e}"

# Default route
@app.route('/')
def home():
    return 'Welcome to my Flask App!'

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
