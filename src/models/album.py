from src.models.album_songs import AlbumSongs


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
        # Save the album to the database
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
        self.album_id = cursor.lastrowid
        print(f"Album {self.name} saved to DB with ID {self.album_id}")

    def get_songs(self, db_connector):
        """
        Retrieves all songs associated with this album.
        """
        album_songs = AlbumSongs(db_connector)
        return album_songs.get_songs_by_album(self.album_id)