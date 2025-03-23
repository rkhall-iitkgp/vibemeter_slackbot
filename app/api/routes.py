from flask import Blueprint, request, jsonify
from app.slack import send_message
from app.database.db import db, Message
import logging
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/send-message', methods=['POST'])
def send_message_endpoint():
    """
    API endpoint to send a message to a Slack user or channel

    Expected JSON payload:
    {
        "user_id": "U123456", 
        "text": "Hello from the API!",
        "channel_id": "C123456" (optional)
    }
    """
    data = request.json

    # Validate request data
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'user_id' not in data:
        return jsonify({"error": "user_id is required"}), 400

    if 'text' not in data:
        return jsonify({"error": "text is required"}), 400

    # Send message
    result = send_message(
        user_id=data['user_id'],
        text=data['text'],
        channel_id=data.get('channel_id')
    )

    if result:
        return jsonify({"success": True, "message": result}), 200
    else:
        return jsonify({"success": False, "error": "Failed to send message"}), 500


@api_bp.route('/messages', methods=['GET'])
def get_messages():
    """
    API endpoint to retrieve stored messages with optional filtering

    Query parameters:
    - user_id: Filter by user ID
    - channel_id: Filter by channel ID
    - limit: Maximum number of results to return (default 100)
    - offset: Offset for pagination (default 0)
    """
    user_id = request.args.get('user_id')
    channel_id = request.args.get('channel_id')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Build query
    query = Message.query

    if user_id:
        query = query.filter(Message.user_id == user_id)

    if channel_id:
        query = query.filter(Message.channel_id == channel_id)

    # Get results with pagination
    messages = query.order_by(Message.timestamp.desc()).limit(
        limit).offset(offset).all()

    # Convert to dict format
    result = [message.to_dict() for message in messages]

    return jsonify({"count": len(result), "messages": result}), 200


@api_bp.route('/slack/events', methods=['POST'])
def slack_events():
    """
    Endpoint for Slack Events API to receive events like messages
    """
    data = request.json
    logger.info(f"Received Slack event: {json.dumps(data)[:100]}...")

    # Handle Slack URL verification challenge
    if data and data.get('type') == 'url_verification':
        return jsonify({"challenge": data.get('challenge')}), 200

    # Handle message events
    if data and data.get('event', {}).get('type') == 'message':
        event = data.get('event', {})

        # Skip bot messages to avoid duplicate storage
        if event.get('bot_id'):
            return jsonify({"success": True, "info": "Skipped bot message"}), 200

        # Get message details
        channel_id = event.get('channel')
        user_id = event.get('user')
        text = event.get('text')
        ts = event.get('ts')

        if channel_id and user_id and text:
            # Store the incoming message
            message = Message(
                user_id=user_id,
                channel_id=channel_id,
                message_text=text,
                message_metadata={
                    "slack_ts": ts,
                    "event_id": data.get('event_id'),
                    "team_id": data.get('team_id'),
                    "direction": "incoming"  # Mark as an incoming message
                }
            )

            db.session.add(message)
            db.session.commit()

            logger.info(
                f"Stored incoming message from {user_id} in channel {channel_id}")

    return jsonify({"success": True}), 200
