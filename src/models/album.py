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

    def save_to_db(self, db):
        cursor = db.connection.cursor()
        query = """
            INSERT INTO albums (
                name, artist_id, spotify_id, number_related_on_release_position,
                spotify_url, youtube_id, youtube_url, youtube_music_id, youtube_music_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            self.name, self.artist_id, self.spotify_album_id, self.number_related_on_release_position,
            self.spotify_url, self.youtube_id, self.youtube_url, self.youtube_music_id, self.youtube_music_url
        ))
        db.connection.commit()

    def update_in_db(self, db, album_id):
        cursor = db.connection.cursor()
        query = """
            UPDATE albums SET
                name = %s, artist_id = %s, spotify_id = %s, number_related_on_release_position = %s,
                spotify_url = %s, youtube_id = %s, youtube_url = %s, youtube_music_id = %s, youtube_music_url = %s
            WHERE album_id = %s
        """
        cursor.execute(query, (
            self.name, self.artist_id, self.spotify_album_id, self.number_related_on_release_position,
            self.spotify_url, self.youtube_id, self.youtube_url, self.youtube_music_id, self.youtube_music_url, album_id
        ))
        db.connection.commit()

    @staticmethod
    def delete_from_db(db, album_id):
        cursor = db.connection.cursor()
        query = "DELETE FROM albums WHERE album_id = %s"
        cursor.execute(query, (album_id,))
        db.connection.commit()

    @staticmethod
    def get_by_id(db, album_id):
        cursor = db.connection.cursor()
        query = "SELECT * FROM albums WHERE album_id = %s"
        cursor.execute(query, (album_id,))
        result = cursor.fetchone()
        if result:
            return Album(**result)
        return None

    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor()
        query = "SELECT * FROM albums"
        cursor.execute(query)
        return [Album(**row) for row in cursor.fetchall()]