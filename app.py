#!/usr/bin/env python
"""
Main entry point for the VibeMeter Slack Bot application
"""

# Load .env file
from pathlib import Path
from dotenv import load_dotenv
from app import create_app
import logging
import os

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the application
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting VibeMeter Slack Bot on port {port}")

    # Check for required environment variables
    if not os.environ.get('SLACK_BOT_TOKEN'):
        logger.warning(
            "SLACK_BOT_TOKEN not found in environment variables. The bot will not be able to send messages.")

    if not os.environ.get('SLACK_SIGNING_SECRET'):
        logger.warning(
            "SLACK_SIGNING_SECRET not found in environment variables. The Slack Events API will not work.")

    logger.info("SlackClient and SlackEventsAPI configured and running")
    app.run(host="0.0.0.0", port=port, debug=True)
