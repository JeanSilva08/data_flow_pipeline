class Album:
    def __init__(
        self,
        name,
        artist_id,
        number_related_on_release_position=None,
        spotify_album_id=None,
        spotify_url=None,
        youtube_id=None,
        youtube_url=None,
        youtube_music_id=None,
        youtube_music_url=None
    ):
        self.name = name
        self.artist_id = artist_id
        self.number_related_on_release_position = number_related_on_release_position
        self.spotify_album_id = spotify_album_id
        self.spotify_url = spotify_url
        self.youtube_id = youtube_id
        self.youtube_url = youtube_url
        self.youtube_music_id = youtube_music_id
        self.youtube_music_url = youtube_music_url
        self.album_id = None  # Default to None until set later

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()
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
        db_connector.connection.commit()
        print(f"Album {self.name} saved to DB.")
        self.album_id = cursor.lastrowid  # Set album_id from the database

    def update_in_db(self, db_connector, album_id):
        cursor = db_connector.connection.cursor()
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
        db_connector.connection.commit()
        print(f"Album {self.name} updated in DB.")

    def delete_from_db(self, db_connector):
        if not self.album_id:
            raise ValueError("Album ID is not set. Cannot delete album.")

        cursor = db_connector.connection.cursor()
        query = "DELETE FROM albums WHERE album_id = %s"
        cursor.execute(query, (self.album_id,))
        db_connector.connection.commit()
        print(f"Album {self.album_id} deleted from DB.")