from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Connect to database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route (test)
@app.route('/')
def home():
    return "User API is running"

# GET /users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])

# POST /users
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO users (name, email) VALUES (?, ?)',
        (name, email)
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": new_id,
        "name": name,
        "email": email
    }), 201


if __name__ == '__main__':
    app.run(debug=True)