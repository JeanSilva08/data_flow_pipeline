class Album:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.artist_id = kwargs.get("artist_id")
        self.number_related_on_release_position = kwargs.get("number_related_on_release_position")
        self.spotify_album_id = kwargs.get("spotify_album_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_id = kwargs.get("youtube_id")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_id = kwargs.get("youtube_music_id")
        self.youtube_music_url = kwargs.get("youtube_music_url")

    @staticmethod
    def get_by_id(db, album_id):
        """
        Fetch an album by its ID and return it as a dictionary.
        """
        cursor = db.connection.cursor(dictionary=True)  # Use dictionary=True to return a dict
        query = "SELECT * FROM albums WHERE album_id = %s"
        cursor.execute(query, (album_id,))
        result = cursor.fetchone()
        if result:
            return Album(**result)  # Pass the dictionary to the constructor
        return None