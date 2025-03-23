"""
Slack Events API handler using slackeventsapi
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
from flask import Blueprint, jsonify, request
from app.database.db import db, Message
from datetime import datetime


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for other routes if needed
events_bp = Blueprint('slack_events', __name__)

# Initialize the Slack Events API adapter - will be created in init_events function
slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
slack_events_adapter = None


def handle_message(event_data):
    """
    Handle incoming message events from Slack
    """
    # Get message event
    event = event_data.get("event", {})

    # Skip bot messages to avoid loops
    if event.get("bot_id"):
        return

    # Get message details
    channel = event.get("channel")
    user = event.get("user")
    text = event.get("text")
    ts = event.get("ts")
    team_id = event_data.get("team_id")
    event_id = event_data.get("event_id")

    if channel and user and text:
        logger.info(f"Message from {user} in {channel}: {text}")

        # Store message in database
        message = Message(
            user_id=user,
            channel_id=channel,
            message_text=text,
            message_metadata={
                "slack_ts": ts,
                "event_id": event_id,
                "team_id": team_id,
                "direction": "incoming"  # Mark as an incoming message
            }
        )

        db.session.add(message)
        db.session.commit()

        logger.info(
            f"Stored incoming message from {user} in channel {channel}")


def init_events(app):
    """
    Initialize the Slack Events API with the Flask app
    """
    global slack_events_adapter

    try:
        # Create a new SlackEventAdapter with the Flask app
        slack_events_adapter = SlackEventAdapter(
            slack_signing_secret,
            endpoint="/slack/events",  # This will be the internal endpoint
            server=app  # Pass the Flask app here
        )

        # Register message event handler
        slack_events_adapter.on("message")(handle_message)

        # Register the blueprint for any other custom endpoints
        app.register_blueprint(events_bp)

        logger.info("Slack Events API initialized with Flask app")
        return app

    except Exception as e:
        logger.error(f"Error initializing Slack Events API: {e}")
        return app
