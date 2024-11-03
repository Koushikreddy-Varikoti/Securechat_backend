from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
socketio = SocketIO()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Example for local SQLite database

    # Initialize extensions with the app
    socketio.init_app(app)
    db.init_app(app)

    # Import blueprints and register them
    from .routes import main
    from .auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app