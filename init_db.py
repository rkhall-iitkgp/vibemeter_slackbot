#!/usr/bin/env python
"""
Initialize the database for the VibeMeter Slack Bot
"""
import os
import logging
from app import create_app
from app.database.db import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database by dropping and creating all tables"""
    app = create_app()

    with app.app_context():
        logger.info("Dropping all existing tables...")
        db.drop_all()

        logger.info("Creating database tables...")
        db.create_all()

        logger.info("Database initialization complete!")


if __name__ == "__main__":
    init_db()
