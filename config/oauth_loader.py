import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OAuthLoader:
    def __init__(self, oauth_file_path):
        """
        Initialize the OAuthLoader with the path to the oauth.json file.
        """
        self.oauth_file_path = oauth_file_path

    def load_oauth_config(self):
        """
        Load the OAuth configuration from the JSON file and environment variables.
        """
        try:
            logger.info(f"Loading OAuth configuration from {self.oauth_file_path}")

            # Load the base configuration from the JSON file
            with open(self.oauth_file_path, 'r') as f:
                oauth_config = json.load(f)

            # Validate and load Google OAuth credentials
            google_config = oauth_config.get('google', {})
            google_config['access_token'] = self._get_env_variable('GOOGLE_ACCESS_TOKEN')
            google_config['refresh_token'] = self._get_env_variable('GOOGLE_REFRESH_TOKEN')
            google_config['expires_at'] = int(self._get_env_variable('GOOGLE_EXPIRES_AT'))
            google_config['expires_in'] = int(self._get_env_variable('GOOGLE_EXPIRES_IN'))

            # Validate and load Spotify OAuth credentials
            spotify_config = oauth_config.get('spotify', {})
            spotify_config['client_id'] = self._get_env_variable('SPOTIFY_CLIENT_ID')
            spotify_config['client_secret'] = self._get_env_variable('SPOTIFY_CLIENT_SECRET')

            logger.info("OAuth configuration loaded successfully")
            return oauth_config
        except Exception as e:
            logger.error(f"Error loading OAuth configuration: {e}")
            raise

    def _get_env_variable(self, key):
        """
        Retrieve an environment variable and raise an error if it is missing.
        """
        value = os.getenv(key)
        if value is None:
            error_msg = f"Missing required environment variable: {key}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return value


# Example usage
if __name__ == "__main__":
    try:
        oauth_loader = OAuthLoader('config/oauth.json')
        oauth_config = oauth_loader.load_oauth_config()
        print(json.dumps(oauth_config, indent=4))
    except Exception as e:
        logger.error(f"Error: {e}")