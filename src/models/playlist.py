


class Playlist:
    def __init__(self, name, spotify_playlist_id=None):
        self.name = name
        self.spotify_playlist_id = spotify_playlist_id
        self.song_ids = []

    def save_to_db(self, db_connector, song_ids):
        cursor = db_connector.connection.cursor()
        query = "INSERT INTO playlists (name, spotify_playlist_id) VALUES (%s, %s)"
        cursor.execute(query, (self.name, self.spotify_playlist_id))

        # Get the last inserted playlist ID
        playlist_id = cursor.lastrowid
        db_connector.connection.commit()

        self.add_songs_to_playlist(db_connector, playlist_id, song_ids)
        print(f"Playlist {self.name} saved to DB with ID {playlist_id}.")

    def update_in_db(self, db_connector, playlist_id, song_ids):
        cursor = db_connector.connection.cursor()
        query = "UPDATE playlists SET name = %s, spotify_playlist_id = %s WHERE playlist_id = %s"
        cursor.execute(query, (self.name, self.spotify_playlist_id, playlist_id))
        db_connector.connection.commit()

        self.add_songs_to_playlist(db_connector, playlist_id, song_ids)
        print(f"Playlist {self.name} updated in DB.")

    @staticmethod
    def delete_from_db(db_connector, playlist_id):
        cursor = db_connector.connection.cursor()
        query = "DELETE FROM playlists WHERE playlist_id = %s"
        cursor.execute(query, (playlist_id,))
        db_connector.connection.commit()
        print(f"Playlist {playlist_id} deleted from DB.")

    def add_songs_to_playlist(self, db_connector, playlist_id, song_ids):
        cursor = db_connector.connection.cursor()
        for song_id in song_ids:
            query = "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)"
            cursor.execute(query, (playlist_id, song_id))
        db_connector.connection.commit()
        print(f"Songs added to playlist {playlist_id}.")

    @classmethod
    def add_playlist_from_spotify(cls, db_connector, spotify_playlist_id, playlist_name=None):
        from src.apis.spotify_api import fetch_playlist_data
        try:
            # Fetch playlist data from Spotify
            playlist_data = fetch_playlist_data(spotify_playlist_id)

            # Use the playlist name from Spotify if none was provided
            playlist_name = playlist_name or playlist_data['name']
            print(f"\nPlaylist Name: {playlist_name}")

            # Print songs in the playlist
            print("\nSongs in the playlist:")
            song_ids = []
            for idx, track_item in enumerate(playlist_data['tracks']['items'], 1):
                track = track_item['track']
                song_name = track['name']
                main_artist = track['artists'][0]['name']
                print(f"{idx}. {song_name} by {main_artist}")

                # Optional: Fetch song ID if it exists in your database, else add it
                # For now, we'll assume the song does not exist and assign a dummy ID
                song_ids.append(idx)  # Dummy song IDs for now

            # Create a new playlist instance and save it to the database
            new_playlist = cls(name=playlist_name, spotify_playlist_id=spotify_playlist_id)
            new_playlist.save_to_db(db_connector, song_ids)

        except Exception as e:
            print(f"Error fetching playlist from Spotify: {e}")
