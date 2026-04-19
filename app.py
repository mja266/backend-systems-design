# Import Flask so we can create the main application
from flask import Flask

# Import the users blueprint and the database initializer from routes/users.py
from routes.users import users_bp, init_db

# Import the tasks blueprint from routes/tasks.py
from routes.tasks import tasks_bp

# Create the Flask app object
app = Flask(__name__)

# Run database setup when the app starts
# This creates the tables if they do not already exist
init_db()

# Register the users blueprint so /users routes become active
app.register_blueprint(users_bp)

# Register the tasks blueprint so /tasks routes become active
app.register_blueprint(tasks_bp)

# Simple root route to confirm the backend is running
@app.route('/')
def home():
    return "Backend API running"

# Run the Flask development server when this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)