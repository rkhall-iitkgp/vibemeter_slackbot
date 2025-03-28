# VibeMeter Slack Bot

A Slack bot that stores and analyzes messages from Slack using SlackClient and SlackEventsAPI.

## Features

- Store outgoing and incoming messages from Slack
- Query stored messages via API
- Send messages to Slack channels and users
- Receive events from Slack in real-time

## Installation

1. Clone the repository
2. Create a virtual environment and activate it
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install requirements
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and update the variables
5. Initialize the database
   ```
   python init_db.py
   ```
6. Run the application
   ```
   python app.py
   ```

## Slack App Configuration

To use this application, you need to create a Slack app:

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and create a new app
2. Add the required OAuth scopes:
   - `chat:write` (for sending messages)
   - `channels:history` (for accessing channel messages)
   - `im:history` (for accessing direct messages)
3. Install the app to your workspace
4. Copy the Bot User OAuth Token (starts with `xoxb-`) to your `.env` file as `SLACK_BOT_TOKEN`
5. Copy the Signing Secret from the "Basic Information" page to your `.env` file as `SLACK_SIGNING_SECRET`

## Configuring Slack Events API (for receiving messages)

To receive messages from Slack:

1. Make your application publicly accessible with a secure URL (HTTPS)
   - For development, you can use a tool like [ngrok](https://ngrok.com/) to create a tunnel
   - Example: `ngrok http 5000`

2. In your Slack App settings:
   - Go to "Event Subscriptions"
   - Enable Events = On
   - Set the Request URL to your public URL + `/events` 
     - Example: `https://your-ngrok-url.ngrok.io/events`
   - Wait for Slack to verify your endpoint

3. Subscribe to Bot Events:
   - Add `message.channels` (to receive messages in public channels)
   - Add `message.im` (to receive direct messages)
   - Add `message.groups` (to receive messages in private channels)

4. Reinstall your app to update permissions if needed

5. Start your application and test sending messages to your bot or in channels where your bot is present

## API Endpoints

### Sending Messages

Send a message to a Slack channel or user:

```
POST /api/send-message
```

Request body:
```json
{
  "user_id": "U12345678",
  "text": "Hello from the API!",
  "channel_id": "C12345678"  // Optional
}
```

### Retrieving Messages

Get all stored messages:

```
GET /api/messages
```

Get messages with query parameters:

```
GET /api/messages?limit=10&user_id=U12345678&channel_id=C12345678&direction=outgoing
```

## Example Scripts

Check the `examples/` directory for example scripts:

1. `send_message.py` - Example of sending a message to Slack
2. `query_messages.py` - Example of querying stored messages

### Usage:

```
python examples/send_message.py --channel C12345678 --text "Hello from the script!"
```

```
python examples/query_messages.py --user U12345678 --channel C12345678 --limit 20
```

## Project Structure

```
├── app/                        # Main application package
│   ├── __init__.py             # App initialization
│   ├── database/               # Database module
│   │   ├── __init__.py         # Database initialization
│   │   └── db.py               # Database models and configuration
│   ├── api/                    # API endpoints
│   │   ├── __init__.py         # API blueprint initialization
│   │   └── routes.py           # API routes
│   └── slack/                  # Slack integration module
│       ├── __init__.py         # Slack module initialization
│       ├── client.py           # Slack client for sending messages
│       └── events.py           # SlackEventsAPI handler
├── examples/                   # Example scripts
│   ├── query_messages.py       # Example script for querying messages 
│   └── send_message.py         # Example script for sending messages
├── .env.example                # Example environment variables
├── app.py                      # Application entry point
├── init_db.py                  # Database initialization script
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```