import os
import logging
from dotenv import load_dotenv
from app import create_app
import click
from flask.cli import with_appcontext
from app.database.db import db

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = create_app()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')


# Add the command to the CLI
app.cli.add_command(init_db_command)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    logger.info("Socket Mode will connect automatically on first request")

    if not os.environ.get('SLACK_APP_TOKEN'):
        logger.warning(
            "SLACK_APP_TOKEN not found in environment variables. Socket Mode will not work.")
    if not os.environ.get('SLACK_BOT_TOKEN'):
        logger.warning(
            "SLACK_BOT_TOKEN not found in environment variables. Bot functionality will not work.")

    app.run(host='0.0.0.0', port=port, debug=True)
