"""
Slack client for interacting with the Slack API
"""
import os
import logging
from slack import WebClient
from slack.errors import SlackApiError
from app.database.db import db, Message
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Slack client with the bot token
slack_client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


def send_message(user_id, text, channel_id=None):
    """
    Send a message to a user or channel via Slack

    Args:
        user_id (str): The Slack user ID
        text (str): The message text
        channel_id (str, optional): The channel ID. If not provided, sends DM to user_id

    Returns:
        dict: The response from the Slack API
    """
    try:
        # If no channel_id is provided, send a direct message to the user
        if not channel_id:
            # Open a DM channel with the user
            response = slack_client.conversations_open(users=user_id)
            channel_id = response['channel']['id']

        # Send the message
        result = slack_client.chat_postMessage(
            channel=channel_id,
            text=text
        )

        # Store the sent message in the database
        message = Message(
            user_id=user_id,
            channel_id=channel_id,
            message_text=text,
            message_metadata={
                "slack_ts": result.get("ts"),
                "direction": "outgoing"  # Mark as an outgoing message
            }
        )

        db.session.add(message)
        db.session.commit()

        logger.info(f"Message sent to {channel_id}")
        return result

    except SlackApiError as e:
        logger.error(f"Error sending message: {e.response['error']}")
        return None
