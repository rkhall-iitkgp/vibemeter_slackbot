import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from app.database.db import db, Message
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Slack client
slack_token = os.environ.get("SLACK_BOT_TOKEN")
slack_client = WebClient(token=slack_token)


def send_message(user_id, text, channel_id=None):
    """
    Send a message to a user or channel and store it in the database

    Args:
        user_id (str): The Slack user ID to send the message to
        text (str): The message text to send
        channel_id (str, optional): The channel ID to send the message to. 
                                   If not provided, sends a direct message to the user.

    Returns:
        dict: The stored message object
    """
    try:
        # Determine target channel (DM or specified channel)
        target_channel = channel_id if channel_id else user_id

        # Send message to Slack
        response = slack_client.chat_postMessage(
            channel=target_channel,
            text=text
        )

        # Store the message in the database
        message = Message(
            user_id=user_id,
            channel_id=target_channel,
            message_text=text,
            message_metadata={
                "slack_ts": response["ts"],
                "is_direct": not bool(channel_id),
                "direction": "outgoing"  # Mark as an outgoing message
            }
        )

        db.session.add(message)
        db.session.commit()

        logger.info(f"Message sent to {target_channel} and stored in database")
        return message.to_dict()

    except SlackApiError as e:
        logger.error(f"Error sending message: {e.response['error']}")
        return None
