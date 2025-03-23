#!/usr/bin/env python
"""
Example script to send messages to Slack using slackclient
"""
import os
import sys
import argparse
import requests
import json
from slack import WebClient
from slack.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def send_direct_message(user_id, text):
    """Send a direct message to a user using slackclient"""
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

    try:
        # Open a direct message channel
        response = client.conversations_open(users=user_id)
        channel_id = response['channel']['id']

        # Send message
        result = client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        print(f"Message sent to user {user_id} via DM")
        return result
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
        return None


def send_channel_message(channel_id, text):
    """Send a message to a channel using slackclient"""
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

    try:
        # Send message
        result = client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        print(f"Message sent to channel {channel_id}")
        return result
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
        return None


def send_via_api(user_id, text, channel_id=None):
    """Send a message using the app's API endpoint"""
    api_url = os.environ.get(
        "API_URL", "http://localhost:5000/api/send-message")

    payload = {
        "user_id": user_id,
        "text": text
    }

    if channel_id:
        payload["channel_id"] = channel_id

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            print(f"Message successfully sent via API")
        else:
            print(f"Error sending message via API: {result.get('error')}")

        return result
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Send a message to Slack")
    parser.add_argument("--user", help="User ID to send the message to")
    parser.add_argument("--channel", help="Channel ID to send the message to")
    parser.add_argument("--text", required=True, help="Message text to send")
    parser.add_argument("--api", action="store_true",
                        help="Use the API endpoint instead of direct client")

    args = parser.parse_args()

    if not args.user and not args.channel:
        print("Error: You must specify either a user or a channel")
        parser.print_help()
        sys.exit(1)

    if args.api:
        # Send via API
        send_via_api(args.user, args.text, args.channel)
    else:
        # Send via client directly
        if args.channel:
            send_channel_message(args.channel, args.text)
        else:
            send_direct_message(args.user, args.text)


if __name__ == "__main__":
    main()
