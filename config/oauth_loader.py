import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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
            with open(self.oauth_file_path, 'r') as f:
                oauth_config = json.load(f)

            # Load sensitive data from environment variables
            oauth_config['google']['access_token'] = os.getenv('GOOGLE_ACCESS_TOKEN')
            oauth_config['google']['refresh_token'] = os.getenv('GOOGLE_REFRESH_TOKEN')
            oauth_config['google']['expires_at'] = int(os.getenv('GOOGLE_EXPIRES_AT', 0))
            oauth_config['google']['expires_in'] = int(os.getenv('GOOGLE_EXPIRES_IN', 0))

            oauth_config['spotify']['client_id'] = os.getenv('SPOTIFY_CLIENT_ID')
            oauth_config['spotify']['client_secret'] = os.getenv('SPOTIFY_CLIENT_SECRET')

            return oauth_config
        except Exception as e:
            raise Exception(f"Error loading OAuth configuration: {e}")


# Example usage
if __name__ == "__main__":
    oauth_loader = OAuthLoader('config/oauth.json')
    oauth_config = oauth_loader.load_oauth_config()
    print(json.dumps(oauth_config, indent=4))