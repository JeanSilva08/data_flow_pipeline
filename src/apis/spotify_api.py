import requests
from datetime import datetime
from src.models.song import Song
from config.config import Config


class SpotifyAPI:
    def __init__(self):
        self.token = self._get_access_token()

    def _get_access_token(self):
        """
        Fetch and return the Spotify API access token.
        """
        client_id = Config.OAUTH_CONFIG['spotify']['client_id']
        client_secret = Config.OAUTH_CONFIG['spotify']['client_secret']

        auth_url = 'https://accounts.spotify.com/api/token'
        response = requests.post(auth_url, data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        })

        if response.status_code != 200:
            raise Exception("Failed to authenticate with Spotify API")

        return response.json()['access_token']

    def fetch_artist_data(self, artist_id):
        """
        Fetch artist details from Spotify.
        """
        url = f'https://api.spotify.com/v1/artists/{artist_id}'
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch artist data: {response.status_code} {response.text}")

        artist_data = response.json()
        return {
            "artist_id": artist_id,
            "song_count": len(artist_data.get('albums', {}).get('items', [])),
            "followers": artist_data['followers']['total'],
            "timestamp": datetime.now()
        }

    def fetch_and_store_artist_data(self, db_connector, artist_id):
        """
        Fetch artist data from Spotify and store it in the database.
        """
        try:
            artist_data = self.fetch_artist_data(artist_id)
            self.store_artist_data(db_connector, artist_data['artist_id'], artist_data['song_count'], artist_data['followers'])
            print(f"Data for artist {artist_id} saved successfully.")
        except Exception as e:
            print(f"Error fetching and storing data for artist {artist_id}: {e}")

    def store_artist_data(self, db_connector, artist_id, song_count, followers):
        """
        Store artist data in the database.
        """
        cursor = db_connector.connection.cursor()
        query = """
            INSERT INTO spotify_artist_data (artist_id, song_count, followers, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (artist_id, song_count, followers, datetime.now()))
        db_connector.connection.commit()

    def fetch_and_store_songs_by_artist(self, db_connector, artist_spotify_id):
        """
        Fetch and store all songs for a given artist.
        """
        try:
            albums = self.fetch_albums_by_artist(artist_spotify_id)
            print(f"Found {len(albums)} albums for artist {artist_spotify_id}.")

            for album in albums:
                album_id = album['id']
                album_name = album['name']
                tracks = self.fetch_tracks_by_album(album_id)
                print(f"Found {len(tracks)} tracks in album '{album_name}'. Adding to database...")

                for track in tracks:
                    track_name = track['name']
                    spotify_track_id = track['id']

                    # Insert track into database
                    new_song = Song(
                        name=track_name,
                        main_artist_id=None,  # Update this if you have artist mapping
                        spotify_id=spotify_track_id,
                        youtube_id=None,  # Leave as None for now
                        featured_artists=[]  # Handle featured artists if needed
                    )
                    new_song.save_to_db(db_connector)
                    print(f"Added track '{track_name}' to the database.")

        except Exception as e:
            print(f"Error fetching and adding songs: {e}")

    def fetch_albums_by_artist(self, artist_spotify_id):
        """
        Fetch all albums for a given artist.
        """
        url = f'https://api.spotify.com/v1/artists/{artist_spotify_id}/albums'
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch albums for artist {artist_spotify_id}: {response.status_code} {response.text}")

        return response.json()['items']

    def fetch_tracks_by_album(self, album_id):
        """
        Fetch all tracks for a given album.
        """
        url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch tracks for album {album_id}: {response.status_code} {response.text}")

        return response.json()['items']


# Export functions for backward compatibility
def fetch_and_store_artist_data(db_connector, artist_id):
    spotify_api = SpotifyAPI()
    spotify_api.fetch_and_store_artist_data(db_connector, artist_id)


def fetch_and_store_songs_by_artist(db_connector, artist_spotify_id):
    spotify_api = SpotifyAPI()
    spotify_api.fetch_and_store_songs_by_artist(db_connector, artist_spotify_id)