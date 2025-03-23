from flask import Flask
from app.database import db
from app.slack import slack_client, start_socket_mode
from app.api import api_bp
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config=None):
    app = Flask(__name__)

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    )

    # Apply any provided configuration
    if config:
        app.config.update(config)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Start Socket Mode client (if not in testing mode)
    if not config or not config.get('TESTING', False):
        socket_client = None

        @app.before_request
        def ensure_socket_mode():
            nonlocal socket_client
            if socket_client is None:
                logger.info("Starting Socket Mode client on first request...")
                socket_client = start_socket_mode(app)

    return app
