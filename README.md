# Vibemeter Slackbot

A Slack bot that sends messages to users when an API endpoint is hit and stores all chat interactions in a database for analysis.

## Features

- Send messages to users or channels via API endpoint
- Store all message interactions in SQLite database (both incoming and outgoing)
- Query stored messages with filtering options
- Listen for incoming Slack messages using Socket Mode and store them automatically

## Installation

1. Clone this repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy the example environment file and fill in your own values:
   ```
   cp .env.example .env
   ```
5. Initialize the database:
   ```
   python init_db.py
   ```

## Slack Configuration

1. Create a new Slack app at [api.slack.com/apps](https://api.slack.com/apps)
2. Add the following OAuth scopes:
   - `chat:write`
   - `im:write`
   - `channels:read`
   - `users:read`
   - `channels:history` (to receive channel messages)
   - `im:history` (to receive direct messages)
   - `groups:history` (to receive private channel messages)

### Socket Mode Configuration

Socket Mode allows your app to receive events from Slack without exposing a public HTTP endpoint:

1. In your Slack App settings, go to "Socket Mode" and toggle it ON
2. Generate an App-Level Token with the `connections:write` scope
3. Copy the token (starts with `xapp-`) and add it to your `.env` file as `SLACK_APP_TOKEN`

4. Go to "Event Subscriptions" and:
   - Enable events (toggle to ON)
   - Under "Subscribe to bot events", add:
     - `message.channels` (to receive messages in public channels)
     - `message.im` (to receive direct messages)
     - `message.groups` (for private channels)
   - No need to provide a Request URL as you're using Socket Mode

5. Reinstall your app to apply the new permissions

6. Copy the Bot User OAuth Token to your `.env` file as `SLACK_BOT_TOKEN`

## Database Configuration

The application uses SQLite by default. The database file is created at `vibemeter.db` in the project root directory.

To customize the database location, set the following environment variable in your `.env` file:
```
DATABASE_URI=sqlite:///path/to/your/custom.db
```

## Running the Application

```
python app.py
```

The server will start at `http://localhost:5000` and automatically connect to Slack's WebSocket API.

## API Endpoints

### Send Message

Send a message to a user or channel:

```
POST /api/send-message
```

Request body:
```json
{
  "user_id": "U12345678",
  "text": "Hello from the API!",
  "channel_id": "C12345678" // Optional - if not provided, sends DM to user_id
}
```

### Get Messages

Retrieve stored messages with optional filtering:

```
GET /api/messages?user_id=U12345678&channel_id=C12345678&limit=10&offset=0
```

Query parameters:
- `user_id`: Filter by user ID (optional)
- `channel_id`: Filter by channel ID (optional)
- `limit`: Maximum number of results to return (default 100)
- `offset`: Offset for pagination (default 0)

## Example Scripts

In the `examples` directory, you'll find example scripts that demonstrate how to use the API:

### Sending Messages

```bash
python examples/send_message.py --user U12345678 --text "Hello from the API!"
```

To send to a channel instead of a direct message:
```bash
python examples/send_message.py --user U12345678 --channel C12345678 --text "Hello channel!"
```

### Querying Messages

To get the last 10 messages:
```bash
python examples/query_messages.py
```

To filter by user and/or channel:
```bash
python examples/query_messages.py --user U12345678 --channel C12345678 --limit 20
```

## Testing Socket Mode

To verify that Socket Mode is working correctly:

1. Make sure your environment variables are properly set in your `.env` file:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   ```

2. Run the Socket Mode test script:
   ```
   python examples/test_socket_mode.py
   ```

3. The script will connect to Slack's Socket Mode API and start listening for events.

4. Send a message in a channel where your bot is present or send a direct message to your bot.

5. You should see log messages showing the incoming events. If you see message events being logged, Socket Mode is working properly.

6. Press Ctrl+C to exit the test script.

If the test script runs without errors and displays incoming messages, your Socket Mode configuration is correct. You can then run the full application which will use Socket Mode for event handling.

## Project Structure

```
├── app/                        # Main application package
│   ├── __init__.py             # App initialization
│   ├── schema.py               # Database schema definition
│   ├── models.py               # Database models
│   ├── api/                    # API endpoints
│   │   ├── __init__.py         # API blueprint initialization
│   │   └── routes.py           # API routes
│   ├── db.py                   # Database module
│   └── slack/                  # Slack integration module
│       ├── __init__.py         # Slack module initialization
│       ├── client.py           # Slack client for sending messages
│       └── socket_handler.py   # Socket Mode handler for Slack events
├── examples/                    # Example scripts
│   ├── query_messages.py        # Example script for querying messages 
│   ├── send_message.py          # Example script for sending messages
│   └── test_socket_mode.py      # Test script for Socket Mode
├── .env.example                 # Example environment variables
├── app.py                       # Application entry point
├── init_db.py                   # Database initialization script
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
``` #   v i b e m e t e r _ s l a c k b o t  
 