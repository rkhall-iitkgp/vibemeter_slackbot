import os
import logging
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient
from app.database.db import db, Message
import json
from datetime import datetime
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Slack clients
bot_token = os.environ.get("SLACK_BOT_TOKEN")
# App-level token for Socket Mode
app_token = os.environ.get("SLACK_APP_TOKEN")
web_client = WebClient(token=bot_token)


def handle_message_events(client, req):
    """
    Process and store message events from Slack
    """
    # Acknowledge the request immediately
    client.send_socket_mode_response(
        SocketModeResponse(envelope_id=req.envelope_id))

    # Process the event data
    if req.payload and "event" in req.payload:
        event = req.payload["event"]

        # Only process message events
        if event and event.get("type") == "message":
            # Skip bot messages to avoid duplicate storage
            if event.get("bot_id") or event.get("subtype") == "bot_message":
                logger.info("Skipped bot message")
                return

            # Get message details
            channel_id = event.get("channel")
            user_id = event.get("user")
            text = event.get("text")
            ts = event.get("ts")

            if channel_id and user_id and text:
                try:
                    # Create database session
                    from flask import current_app
                    with current_app.app_context():
                        # Store the incoming message
                        message = Message(
                            user_id=user_id,
                            channel_id=channel_id,
                            message_text=text,
                            message_metadata={
                                "slack_ts": ts,
                                "event_id": req.payload.get("event_id"),
                                "team_id": req.payload.get("team_id"),
                                "direction": "incoming"  # Mark as an incoming message
                            }
                        )

                        db.session.add(message)
                        db.session.commit()

                        logger.info(
                            f"Stored incoming message from {user_id} in channel {channel_id}")
                except Exception as e:
                    logger.error(f"Error storing message: {str(e)}")


def start_socket_mode(app):
    """
    Start the Socket Mode client in a separate thread

    Args:
        app: Flask application instance for context
    """
    if not app_token:
        logger.warning(
            "SLACK_APP_TOKEN not found in environment. Socket Mode will not start.")
        return None

    if not bot_token:
        logger.warning(
            "SLACK_BOT_TOKEN not found in environment. Socket Mode will not start.")
        return None

    # Initialize the Socket Mode client
    client = SocketModeClient(
        app_token=app_token,
        web_client=web_client
    )

    # Add event listeners
    client.socket_mode_request_listeners.append(handle_message_events)

    # Start Socket Mode client in a separate thread
    def start_client():
        logger.info("Starting Slack Socket Mode client...")
        with app.app_context():
            client.connect()

    thread = threading.Thread(target=start_client, daemon=True)
    thread.start()

    logger.info("Socket Mode client started in background thread")
    return client
