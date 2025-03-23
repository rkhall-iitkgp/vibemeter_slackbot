#!/usr/bin/env python
"""
Example script to query stored messages from the Slack bot API.
"""
import requests
import json
import argparse
from datetime import datetime


def query_messages(api_url, user_id=None, channel_id=None, limit=10, offset=0):
    """
    Query stored messages from the Slack bot API

    Args:
        api_url (str): Base URL of the API (e.g., http://localhost:5000)
        user_id (str, optional): Filter by Slack user ID
        channel_id (str, optional): Filter by channel ID
        limit (int, optional): Maximum number of results to return
        offset (int, optional): Offset for pagination

    Returns:
        dict: API response
    """
    # Build query parameters
    params = {}
    if user_id:
        params["user_id"] = user_id
    if channel_id:
        params["channel_id"] = channel_id

    params["limit"] = limit
    params["offset"] = offset

    # Make the API request
    response = requests.get(
        f"{api_url}/api/messages",
        params=params
    )

    # Parse the response
    result = response.json()

    if response.status_code == 200:
        if result["count"] == 0:
            print("No messages found matching your criteria.")
        else:
            print(f"Found {result['count']} message(s):")
            for idx, msg in enumerate(result["messages"], 1):
                # Format timestamp
                timestamp = datetime.fromisoformat(msg["timestamp"])
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                # Print message details
                print(f"\n--- Message {idx} ---")
                print(f"ID: {msg['id']}")
                print(f"From/To: User {msg['user_id']} in {msg['channel_id']}")
                print(f"Time: {formatted_time}")
                print(f"Content: {msg['message_text']}")
    else:
        print(
            f"❌ Failed to query messages: {result.get('error', 'Unknown error')}")

    return result


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Query messages from the Slack bot API")
    parser.add_argument(
        "--api", default="http://localhost:5000", help="API base URL")
    parser.add_argument("--user", help="Filter by Slack user ID")
    parser.add_argument("--channel", help="Filter by channel ID")
    parser.add_argument("--limit", type=int, default=10,
                        help="Maximum number of results to return")
    parser.add_argument("--offset", type=int, default=0,
                        help="Offset for pagination")

    args = parser.parse_args()

    # Query messages
    query_messages(args.api, args.user, args.channel, args.limit, args.offset)
