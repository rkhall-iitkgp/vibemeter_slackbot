#!/usr/bin/env python
"""
Example script to demonstrate sending a message via the Slack bot API.
"""
import requests
import json
import argparse


def send_message(api_url, user_id, text, channel_id=None):
    """
    Send a message to a Slack user or channel using the API

    Args:
        api_url (str): Base URL of the API (e.g., http://localhost:5000)
        user_id (str): Slack user ID to send the message to
        text (str): Message text
        channel_id (str, optional): Channel ID to send to instead of direct message

    Returns:
        dict: API response
    """
    # Build the request payload
    payload = {
        "user_id": user_id,
        "text": text
    }

    if channel_id:
        payload["channel_id"] = channel_id

    # Make the API request
    response = requests.post(
        f"{api_url}/api/send-message",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    # Parse the response
    result = response.json()

    if response.status_code == 200 and result.get("success"):
        print(f"✅ Message sent successfully!")
        print(f"Message ID: {result['message']['id']}")
        print(
            f"Recipient: {'Channel' if channel_id else 'User'} {result['message']['channel_id']}")
    else:
        print(
            f"❌ Failed to send message: {result.get('error', 'Unknown error')}")

    return result


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Send a message via the Slack bot API")
    parser.add_argument(
        "--api", default="http://localhost:5000", help="API base URL")
    parser.add_argument("--user", required=True,
                        help="Slack user ID to message")
    parser.add_argument(
        "--channel", help="Optional channel ID (if omitted, sends a direct message)")
    parser.add_argument("--text", required=True, help="Message text to send")

    args = parser.parse_args()

    # Send the message
    send_message(args.api, args.user, args.text, args.channel)
