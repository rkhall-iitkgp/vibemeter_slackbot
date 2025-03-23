import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from app.database import db
from app.api import api_bp
from app.slack.events import init_events

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(test_config=None):
    """Create and configure the Flask application"""
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE_URI=os.environ.get('DATABASE_URI', 'sqlite:///messages.db'),
        SERVER_NAME=os.environ.get('SERVER_NAME'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Initialize the database
    db.init_app(app)

    # Register API blueprint
    app.register_blueprint(api_bp)

    # Initialize Slack Events API
    init_events(app)

    # Add a simple test route
    @app.route('/')
    def index():
        return 'VibeMeter Slack Bot is running!'

    logger.info("Application initialized with Slack Events API")

    return app
