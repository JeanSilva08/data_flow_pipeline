from dotenv import load_dotenv
import os
from .oauth_loader import OAuthLoader

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Centralized configuration settings for the application.
    """

    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'mainstreet_data_pipeline')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

    # OAuth Configuration
    OAUTH_CONFIG = OAuthLoader('config/oauth.json').load_oauth_config()

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')  # File to store logs

    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # Enable/disable debug mode
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')  # For session management

    @classmethod
    def validate(cls):
        """
        Validate required configuration settings.
        """
        required_vars = [
            'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
            'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET'
        ]
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Missing required environment variable: {var}")


# Validate configuration on import
Config.validate()