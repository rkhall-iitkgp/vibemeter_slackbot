from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from pathlib import Path

db = SQLAlchemy()


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    channel_id = db.Column(db.String(50), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    message_metadata = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Message {self.id} to {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'channel_id': self.channel_id,
            'message_text': self.message_text,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.message_metadata
        }


def init_app(app):
    """Initialize database with the Flask app"""
    # Configure SQLAlchemy to use SQLite
    db_path = os.environ.get('DATABASE_URI', 'sqlite:///vibemeter.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize
    db.init_app(app)

    # Create all tables
    with app.app_context():
        db.create_all()
