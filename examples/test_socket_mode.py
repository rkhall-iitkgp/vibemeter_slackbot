#!/usr/bin/env python
"""
Test script to verify Socket Mode is working properly.
This script directly connects to Slack's Socket Mode without the Flask app.
"""
import os
import sys
import logging
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.web import WebClient
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get tokens from environment
app_token = os.environ.get("SLACK_APP_TOKEN")
bot_token = os.environ.get("SLACK_BOT_TOKEN")


def process_event(client, req):
    """Process incoming events from Slack"""
    # Acknowledge the request first
    client.send_socket_mode_response(
        SocketModeResponse(envelope_id=req.envelope_id))

    # Log the event type
    logger.info(f"Received event type: {req.type}")

    # If it's an events_api type (like messages)
    if req.type == "events_api":
        event = req.payload.get("event", {})
        event_type = event.get("type")

        logger.info(f"Event details: {event_type}")

        # Handle message events
        if event_type == "message":
            channel = event.get("channel")
            user = event.get("user")
            text = event.get("text")

            if channel and user and text:
                logger.info(f"Message from {user} in {channel}: {text}")

                # Here you would typically store in database
                logger.info(
                    "This message would be stored in the database in the full app")


def main():
    """Main function to test Socket Mode"""
    # Check for required tokens
    if not app_token:
        logger.error(
            "SLACK_APP_TOKEN not found in environment. Please check your .env file.")
        sys.exit(1)

    if not bot_token:
        logger.error(
            "SLACK_BOT_TOKEN not found in environment. Please check your .env file.")
        sys.exit(1)

    if not app_token.startswith("xapp-"):
        logger.warning(
            "Your app token doesn't start with 'xapp-', which is unusual. Please check it.")

    # Initialize clients
    web_client = WebClient(token=bot_token)
    socket_client = SocketModeClient(
        app_token=app_token,
        web_client=web_client,
        logger=logger
    )

    # Register event handler
    socket_client.socket_mode_request_listeners.append(process_event)

    # Connect and start receiving events
    logger.info("Connecting to Slack via Socket Mode... (Press Ctrl+C to exit)")
    socket_client.connect()

    # Keep the script running until interrupted
    try:
        # Just wait for events
        from threading import Event
        Event().wait()
    except KeyboardInterrupt:
        # Gracefully disconnect on Ctrl+C
        logger.info("Disconnecting from Slack Socket Mode...")
        socket_client.disconnect()
        logger.info("Disconnected")


if __name__ == "__main__":
    main()
