import sqlite3

conn = sqlite3.connect('database.db')
# Connect to your SQLite database file

cursor = conn.cursor()
# Create a cursor to run SQL commands

cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
# Add password column to users table

conn.commit()
# Save changes

conn.close()
# Close connection