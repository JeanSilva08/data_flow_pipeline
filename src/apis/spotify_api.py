import requests
import json
import os


def get_access_token():
    # Load client_id and client_secret from oauth.json file
    oauth_path = os.path.join(os.path.dirname(__file__), '../../config/oauth.json')
    with open(oauth_path, 'r') as f:
        credentials = json.load(f)

    client_id = credentials['client_id']
    client_secret = credentials['client_secret']

    # Spotify token URL
    auth_url = 'https://accounts.spotify.com/api/token'

    # Request the access token
    response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    })

    if response.status_code != 200:
        raise Exception("Failed to authenticate with Spotify API")

    # Return the access token
    return response.json()['access_token']


def fetch_playlist_data(playlist_id):
    # Fetch access token
    token = get_access_token()

    # Spotify playlist endpoint
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Request playlist data
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching playlist: {response.status_code}, {response.text}")
