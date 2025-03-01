from src.models.album_songs import AlbumSongs


class Song:
    def __init__(
        self,
        name,
        main_artist_id,
        album_id=None,
        producer=None,
        beatmaker=None,
        record_label=None,
        type=None,
        release_date=None,
        days_from_release=None,
        spotify_id=None,
        youtube_id=None,
        youtube_music_id=None,
        spotify_url=None,
        youtube_url=None,
        youtube_music_url=None,
        featured_artists=None
    ):
        self.name = name
        self.main_artist_id = main_artist_id
        self.album_id = album_id
        self.producer = producer
        self.beatmaker = beatmaker
        self.record_label = record_label
        self.type = type
        self.release_date = release_date
        self.days_from_release = days_from_release
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id
        self.youtube_music_id = youtube_music_id
        self.spotify_url = spotify_url
        self.youtube_url = youtube_url
        self.youtube_music_url = youtube_music_url
        self.featured_artists = featured_artists or []

    def save_to_db(self, db_connector):
        cursor = db_connector.connection.cursor()
        song_query = """
            INSERT INTO songs (
                name, main_artist_id, album_id, producer, beatmaker, record_label, type,
                release_date, days_from_release, spotify_id, youtube_id,
                youtube_music_id, spotify_url, youtube_url, youtube_music_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(song_query, (
            self.name, self.main_artist_id, self.album_id, self.producer, self.beatmaker, self.record_label,
            self.type, self.release_date, self.days_from_release, self.spotify_id, self.youtube_id,
            self.youtube_music_id, self.spotify_url, self.youtube_url, self.youtube_music_url
        ))
        song_id = cursor.lastrowid
        if self.album_id:
            album_songs = AlbumSongs(db_connector)
            album_songs.add_song_to_album(self.album_id, song_id)
        if self.featured_artists:
            song_artist_query = "INSERT INTO song_artists (song_id, artist_id) VALUES (%s, %s)"
            for artist_id in self.featured_artists:
                cursor.execute(song_artist_query, (song_id, artist_id))
        db_connector.connection.commit()
        print(f"Song '{self.name}' with ID {song_id} inserted successfully")

    @staticmethod
    def delete_from_db(db_connector, song_id):
        """
        Deletes a song from the database.
        """
        cursor = db_connector.connection.cursor()
        delete_album_songs_query = "DELETE FROM album_songs WHERE song_id = %s"
        cursor.execute(delete_album_songs_query, (song_id,))
        delete_song_artists_query = "DELETE FROM song_artists WHERE song_id = %s"
        cursor.execute(delete_song_artists_query, (song_id,))
        delete_song_query = "DELETE FROM songs WHERE song_id = %s"
        cursor.execute(delete_song_query, (song_id,))
        db_connector.connection.commit()
        print(f"Song with ID {song_id} deleted successfully")

    @classmethod
    def get_by_id(cls, db_connector, song_id):
        cursor = db_connector.connection.cursor(dictionary=True)
        query = "SELECT * FROM songs WHERE song_id = %s"  # Use the correct column name
        cursor.execute(query, (song_id,))
        song_data = cursor.fetchone()

        if song_data:
            return cls(
                name=song_data["name"],
                main_artist_id=song_data["main_artist_id"],
                album_id=song_data["album_id"],
                producer=song_data["producer"],
                beatmaker=song_data["beatmaker"],
                record_label=song_data["record_label"],
                type=song_data["type"],
                release_date=song_data["release_date"],
                days_from_release=song_data["days_from_release"],
                spotify_id=song_data["spotify_id"],
                youtube_id=song_data["youtube_id"],
                youtube_music_id=song_data["youtube_music_id"],
                spotify_url=song_data["spotify_url"],
                youtube_url=song_data["youtube_url"],
                youtube_music_url=song_data["youtube_music_url"],
                featured_artists=[]  # Fetch artists separately if needed
            )
        else:
            return None

    def remove_from_album(self, db_connector, song_id):
        """
        Removes a song from an album using the AlbumSongs class.
        """
        album_songs = AlbumSongs(db_connector)
        album_songs.remove_song_from_album(self.album_id, song_id)
        print(f"Song {song_id} removed from album {self.album_id}")