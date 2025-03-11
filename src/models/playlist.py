class Playlist:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.spotify_playlist_id = kwargs.get("spotify_playlist_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.song_ids = kwargs.get("song_ids", [])

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