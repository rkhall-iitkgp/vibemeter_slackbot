from pathlib import Path
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from app.slack import send_message
from app.database.db import db, Message
import logging
import json

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


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
        "user_id": "U08J1P3FBRD", 
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
        return jsonify({"success": True, "message": "Message sent successfully"}), 200
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
    - direction: Filter by message direction (incoming/outgoing)
    """
    user_id = request.args.get('user_id')
    channel_id = request.args.get('channel_id')
    direction = request.args.get('direction')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Build query
    query = Message.query

    if user_id:
        query = query.filter(Message.user_id == user_id)

    if channel_id:
        query = query.filter(Message.channel_id == channel_id)

    if direction:
        query = query.filter(
            Message.message_metadata.contains({"direction": direction})
        )

    # Get results with pagination
    messages = query.order_by(Message.timestamp.desc()).limit(
        limit).offset(offset).all()

    # Convert to dict format
    result = [message.to_dict() for message in messages]

    return jsonify({"count": len(result), "messages": result}), 200


@api_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify the API is working"""
    return jsonify({"status": "ok", "message": "API is working"}), 200
