from flask import Flask  # Import Flask framework

# Import the users Blueprint
from routes.users import users_bp
from routes.tasks import tasks_bp
# Create Flask app instance
app = Flask(__name__)

# Register the users routes into the main app
app.register_blueprint(users_bp)
app.register_blueprint(tasks_bp)
# Root route (simple test endpoint)
@app.route('/')
def home():
    return "Backend API running"

# Run app locally
if __name__ == '__main__':
    app.run(debug=True)  # debug=True enables auto-reload + error logs
    
