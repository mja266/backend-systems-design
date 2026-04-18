from flask import Flask
from routes.users import users_bp, init_db
from routes.tasks import tasks_bp

app = Flask(__name__)

# Initialize DB
init_db()

# Register routes
app.register_blueprint(users_bp)
app.register_blueprint(tasks_bp)

@app.route('/')
def home():
    return "Backend API running"

if __name__ == '__main__':
    app.run(debug=True)