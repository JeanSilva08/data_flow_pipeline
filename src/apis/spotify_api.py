import requests
import json
import os
from datetime import datetime


def get_access_token():
    oauth_path = os.path.join(os.path.dirname(__file__), '../../config/oauth.json')
    with open(oauth_path, 'r') as f:
        credentials = json.load(f)['spotify']

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

    return response.json()['access_token']


def fetch_spotify_data(artist_id):
    token = get_access_token()

    # Fetch artist details
    url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch artist data: {response.status_code} {response.text}")

    artist_data = response.json()

    # Fetch song count (albums)
    song_count = len(artist_data.get('albums', {}).get('items', []))
    followers = artist_data['followers']['total']

    return {
        "artist_id": artist_id,
        "song_count": song_count,
        "followers": followers,
        "timestamp": datetime.now()
    }


def store_spotify_data(db_connector, artist_id, song_count, followers):
    cursor = db_connector.connection.cursor()
    query = "INSERT INTO spotify_artist_data (artist_id, song_count, followers, timestamp) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (artist_id, song_count, followers, datetime.now()))
    db_connector.connection.commit()


def fetch_and_store_artist_data(db_connector, artist_id):
    try:
        # Fetch data from Spotify
        artist_data = fetch_spotify_data(artist_id)

        # Store the data in the database
        store_spotify_data(db_connector, artist_data['artist_id'], artist_data['song_count'], artist_data['followers'])

        print(f"Data for artist {artist_id} saved successfully.")

    except Exception as e:
        print(f"Error fetching and storing data for artist {artist_id}: {e}")

def fetch_playlist_data(playlist_id):
    token = get_access_token()  # Assuming get_access_token() is already defined

    # Fetch playlist details
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch playlist data: {response.status_code} {response.text}")

    return response.json()

