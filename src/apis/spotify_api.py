import requests
from datetime import datetime, timedelta
from src.models.song import Song
from config.config import Config
import time


def _get_access_token():
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


class SpotifyAPI:
    def __init__(self):
        self.token = _get_access_token()
        self.token_expiry = datetime.now() + timedelta(minutes=55)  # Tokens expire after 1 hour
        self.cache = {}  # Simple cache to store API responses
        self.rate_limit_reset = None  # Track rate limit reset time

    def _check_token_expiry(self):
        """
        Check if the token is about to expire and refresh it if necessary.
        """
        if datetime.now() >= self.token_expiry:
            self.token = _get_access_token()
            self.token_expiry = datetime.now() + timedelta(minutes=55)

    def _make_request(self, url):
        """
        Make a request to the Spotify API with rate limiting and token management.
        """
        self._check_token_expiry()

        if url in self.cache:
            return self.cache[url]

        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers)

        if response.status_code == 429:  # Rate limit exceeded
            reset_time = int(response.headers.get('Retry-After', 1))
            print(f"Rate limit exceeded. Retrying after {reset_time} seconds.")
            time.sleep(reset_time)
            return self._make_request(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")

        self.cache[url] = response.json()  # Cache the response
        return response.json()

    def fetch_artist_data(self, artist_id):
        """
        Fetch artist details from Spotify.
        """
        url = f'https://api.spotify.com/v1/artists/{artist_id}'
        artist_data = self._make_request(url)

        return {
            "artist_id": artist_id,
            "name": artist_data['name'],
            "followers": artist_data['followers']['total'],
            "genres": artist_data['genres'],
            "popularity": artist_data['popularity'],
            "timestamp": datetime.now()
        }

    def fetch_all_artist_info(self, artist_id):
        """
        Fetch all possible information about an artist, including albums and tracks.
        """
        artist_data = self.fetch_artist_data(artist_id)
        albums = self.fetch_albums_by_artist(artist_id)
        tracks = []

        for album in albums:
            album_id = album['id']
            album_tracks = self.fetch_tracks_by_album(album_id)
            tracks.extend(album_tracks)

        return {
            "artist": {
                "artist_id": artist_data['artist_id'],
                "name": artist_data['name'],
                "followers": artist_data['followers'],
                "genres": artist_data['genres'],
                "popularity": artist_data['popularity'],
                "timestamp": artist_data['timestamp'].isoformat()  # Convert datetime to string
            },
            "albums": albums,
            "tracks": tracks
        }


    def fetch_albums_by_artist(self, artist_id):
        """
        Fetch all albums for a given artist.
        """
        url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
        return self._make_request(url)['items']

    def fetch_tracks_by_album(self, album_id):
        """
        Fetch all tracks for a given album.
        """
        url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
        return self._make_request(url)['items']

    @staticmethod
    def store_artist_data(db_connector, artist_data):
        """
        Store artist data in the database.
        """
        cursor = db_connector.connection.cursor()
        query = """
            INSERT INTO spotify_artist_data (artist_id, name, followers, genres, popularity, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            artist_data['artist_id'],
            artist_data['name'],
            artist_data['followers'],
            artist_data['genres'],
            artist_data['popularity'],
            artist_data['timestamp']
        ))
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

    def fetch_and_store_artist_data(self, db_connector, artist_id):
        pass

    def fetch_playlist_data(self, playlist_id):
        """
        Fetch playlist data from Spotify using the playlist ID.
        """
        try:
            # Ensure the token is valid
            self._check_token_expiry()

            # Spotify API endpoint for fetching playlist details
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                playlist_data = response.json()
                return {
                    "name": playlist_data.get("name"),
                    "external_urls": playlist_data.get("external_urls", {}),
                    # Add other fields as needed
                }
            elif response.status_code == 401:  # Unauthorized
                print("Token expired or invalid. Refreshing token...")
                self.token = _get_access_token()  # Refresh the token
                return self.fetch_playlist_data(playlist_id)  # Retry the request
            elif response.status_code == 404:  # Not Found
                print(f"Error: Playlist with ID '{playlist_id}' not found.")
                return {}
            else:
                print(f"Error fetching playlist data: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error in fetch_playlist_data: {e}")
            return {}

# Export functions for backward compatibility
def fetch_and_store_artist_data(db_connector, artist_id):
    """
    Fetch and store artist data from Spotify.
    """
    spotify_api = SpotifyAPI()
    spotify_api.fetch_and_store_artist_data(db_connector, artist_id)


def fetch_and_store_songs_by_artist(db_connector, artist_spotify_id):
    """
    Fetch and store all songs for a given artist.
    """
    spotify_api = SpotifyAPI()

    spotify_api.fetch_and_store_songs_by_artist(db_connector, artist_spotify_id)


