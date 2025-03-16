from src.apis.spotify_api import SpotifyAPI



class Playlist:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.spotify_playlist_id = kwargs.get("spotify_playlist_id")
        self.spotify_url = kwargs.get("spotify_url")

    @staticmethod
    def get_by_id(db, playlist_id):
        """
        Fetch a playlist by its ID and return it as a dictionary.
        """
        cursor = db.connection.cursor(dictionary=True)  # Use dictionary=True to return a dict
        query = "SELECT * FROM playlists WHERE playlist_id = %s"
        cursor.execute(query, (playlist_id,))
        result = cursor.fetchone()
        if result:
            return Playlist(**result)  # Pass the dictionary to the constructor
        return None

    @staticmethod
    def add_playlist_from_spotify(db, spotify_playlist_id, playlist_name=None):
        """
        Add a playlist to the database using data fetched from Spotify.
        """
        try:
            # Fetch playlist data from Spotify
            playlist_data = SpotifyAPI().fetch_playlist_data(spotify_playlist_id)

            # Debug: Print the fetched playlist data
            print("Fetched Playlist Data:", playlist_data)

            # Check if playlist data is valid
            if not playlist_data or "name" not in playlist_data:
                print("Error: Invalid or empty playlist data fetched from Spotify.")
                return

            # If a custom playlist name is provided, use it; otherwise, use the name from Spotify
            name = playlist_name if playlist_name else playlist_data.get("name", "Unnamed Playlist")

            # Debug: Print the final playlist name
            print("Final Playlist Name:", name)

            # Insert the playlist into the database
            query = """
                INSERT INTO playlists (name, spotify_playlist_id, spotify_url)
                VALUES (%s, %s, %s)
            """
            values = (
                name,
                spotify_playlist_id,
                playlist_data.get("external_urls", {}).get("spotify"),
            )
            db.execute_query(query, values)
            print("Playlist added successfully!")
        except Exception as e:
            print(f"Error adding playlist: {e}")

    @staticmethod
    def update_in_db(db, playlist_id, **kwargs):
        """
        Update a playlist's information in the database.
        """
        try:
            # Build the SET clause for the SQL query
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(playlist_id)  # Add playlist_id for the WHERE clause

            query = f"""
                UPDATE playlists
                SET {set_clause}
                WHERE playlist_id = %s
            """
            db.execute_query(query, values)
            print("Playlist updated successfully!")
        except Exception as e:
            print(f"Error updating playlist: {e}")

    @staticmethod
    def delete_from_db(db, playlist_id):
        """
        Delete a playlist from the database.
        """
        try:
            query = "DELETE FROM playlists WHERE playlist_id = %s"
            db.execute_query(query, (playlist_id,))
            print("Playlist deleted successfully!")
        except Exception as e:
            print(f"Error deleting playlist: {e}")