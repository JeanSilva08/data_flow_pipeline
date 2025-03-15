class Album:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.artist_id = kwargs.get("artist_id")
        self.number_related_on_release_position = kwargs.get("number_related_on_release_position")
        self.spotify_album_id = kwargs.get("spotify_album_id")  # Ensure this is included
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_id = kwargs.get("youtube_id")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_id = kwargs.get("youtube_music_id")
        self.youtube_music_url = kwargs.get("youtube_music_url")

    @staticmethod
    def get_by_spotify_id(db, spotify_album_id):
        """
        Fetch an album by its Spotify ID.
        """
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM albums WHERE spotify_album_id = %s"
        cursor.execute(query, (spotify_album_id,))
        result = cursor.fetchone()
        if result:
            return Album(**result)
        return None

    def save_to_db(self, db):
        cursor = db.connection.cursor()
        query = """
            INSERT INTO albums (
                name, artist_id, number_related_on_release_position,
                spotify_album_id, spotify_url, youtube_id, youtube_url,
                youtube_music_id, youtube_music_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            self.name, self.artist_id, self.number_related_on_release_position,
            self.spotify_album_id, self.spotify_url, self.youtube_id,
            self.youtube_url, self.youtube_music_id, self.youtube_music_url
        ))
        db.connection.commit()