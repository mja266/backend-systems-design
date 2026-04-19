import sqlite3  # Import SQLite library to interact with the database

def get_db_connection():
    # Create a connection to the SQLite database file
    conn = sqlite3.connect('database.db')

    # This allows us to access columns by name instead of index
    # Example: row["name"] instead of row[0]
    conn.row_factory = sqlite3.Row

    # Return the connection so other files can use it
    return conn