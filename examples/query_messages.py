#!/usr/bin/env python
"""
Example script to query messages from the Slack bot database
"""
import os
import argparse
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def query_messages(user_id=None, channel_id=None, limit=10, offset=0, direction=None):
    """
    Query messages from the API with optional filtering

    Args:
        user_id (str, optional): Filter by user ID
        channel_id (str, optional): Filter by channel ID
        limit (int, optional): Maximum number of messages to return
        offset (int, optional): Offset for pagination
        direction (str, optional): Filter by message direction (incoming/outgoing)

    Returns:
        dict: API response with messages
    """
    # Build API URL
    api_url = os.environ.get("API_URL", "http://localhost:5000/api/messages")

    # Build query parameters
    params = {"limit": limit, "offset": offset}

    if user_id:
        params["user_id"] = user_id

    if channel_id:
        params["channel_id"] = channel_id

    if direction:
        params["direction"] = direction

    # Make the API request
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        return data
    except requests.exceptions.RequestException as e:
        print(f"Error querying messages: {e}")
        return None


def display_messages(messages_data):
    """
    Display messages in a readable format

    Args:
        messages_data (dict): API response with messages
    """
    if not messages_data:
        print("No data to display")
        return

    count = messages_data.get("count", 0)
    messages = messages_data.get("messages", [])

    print(f"Found {count} messages:")
    print("-" * 60)

    for msg in messages:
        direction = msg.get("message_metadata", {}).get("direction", "unknown")
        direction_icon = "→" if direction == "outgoing" else "←" if direction == "incoming" else "?"

        print(f"{msg.get('timestamp')} {direction_icon} User: {msg.get('user_id')}")
        print(f"Channel: {msg.get('channel_id')}")
        print(f"Text: {msg.get('message_text')}")
        print("-" * 60)


def main():
    """Main function to parse arguments and query messages"""
    parser = argparse.ArgumentParser(
        description="Query messages from the Slack bot database")
    parser.add_argument("--user", help="Filter by user ID")
    parser.add_argument("--channel", help="Filter by channel ID")
    parser.add_argument("--limit", type=int, default=10,
                        help="Maximum number of messages to return")
    parser.add_argument("--offset", type=int, default=0,
                        help="Offset for pagination")
    parser.add_argument(
        "--direction", choices=["incoming", "outgoing"], help="Filter by message direction")

    args = parser.parse_args()

    # Query messages
    messages_data = query_messages(
        user_id=args.user,
        channel_id=args.channel,
        limit=args.limit,
        offset=args.offset,
        direction=args.direction
    )

    # Display messages
    display_messages(messages_data)


if __name__ == "__main__":
    main()
