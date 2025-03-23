import pytest
from app import create_app
from app.database.db import db as _db
import json
import os
from unittest.mock import patch


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })

    with app.app_context():
        _db.create_all()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db


def test_send_message_endpoint_validation(client):
    # Test with no data
    response = client.post('/api/send-message', json={})
    assert response.status_code == 400

    # Test with missing fields
    response = client.post('/api/send-message', json={"user_id": "U123"})
    assert response.status_code == 400

    response = client.post('/api/send-message', json={"text": "Hello"})
    assert response.status_code == 400


@patch('app.slack.client.slack_client.chat_postMessage')
def test_send_message_success(mock_post_message, client, db):
    # Mock successful Slack API response
    mock_post_message.return_value = {"ok": True, "ts": "1234.5678"}

    # Test API endpoint
    response = client.post('/api/send-message', json={
        "user_id": "U123456",
        "text": "Test message"
    })

    # Check results
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["message"]["user_id"] == "U123456"
    assert data["message"]["message_text"] == "Test message"

    # Verify database entry was created
    from app.database.db import Message
    message = Message.query.first()
    assert message is not None
    assert message.user_id == "U123456"
    assert message.message_text == "Test message"


def test_get_messages(client, db):
    # Add some test messages to the database
    from app.database.db import Message

    messages = [
        Message(user_id="U1", channel_id="C1", message_text="Message 1"),
        Message(user_id="U1", channel_id="C2", message_text="Message 2"),
        Message(user_id="U2", channel_id="C1", message_text="Message 3")
    ]

    for msg in messages:
        db.session.add(msg)
    db.session.commit()

    # Test unfiltered
    response = client.get('/api/messages')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["count"] == 3

    # Test filtering by user_id
    response = client.get('/api/messages?user_id=U1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["count"] == 2

    # Test filtering by channel_id
    response = client.get('/api/messages?channel_id=C1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["count"] == 2

    # Test combined filters
    response = client.get('/api/messages?user_id=U1&channel_id=C1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["count"] == 1
