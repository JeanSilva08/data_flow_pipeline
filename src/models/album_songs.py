class AlbumSongs:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def add_song_to_album(self, album_id, song_id):
        """
        Adds a song to an album in the album_songs table.
        """
        cursor = self.db_connector.connection.cursor()
        query = "INSERT INTO album_songs (album_id, song_id) VALUES (%s, %s)"
        cursor.execute(query, (album_id, song_id))
        self.db_connector.connection.commit()
        print(f"Added song {song_id} to album {album_id}")

    def get_songs_by_album(self, album_id):
        """
        Retrieves all songs associated with a specific album.
        """
        cursor = self.db_connector.connection.cursor(dictionary=True)
        query = """
            SELECT songs.* FROM songs
            JOIN album_songs ON songs.song_id = album_songs.song_id
            WHERE album_songs.album_id = %s
        """
        cursor.execute(query, (album_id,))
        return cursor.fetchall()

    def get_albums_for_song(self, song_id):
        """
        Retrieves all albums associated with a specific song.
        """
        cursor = self.db_connector.connection.cursor()
        query = """
            SELECT albums.* FROM albums
            JOIN album_songs ON albums.album_id = album_songs.album_id
            WHERE album_songs.song_id = %s
        """
        cursor.execute(query, (song_id,))
        return cursor.fetchall()

    def remove_song_from_album(self, album_id, song_id):
        """
        Removes a song from an album in the album_songs table.
        """
        cursor = self.db_connector.connection.cursor()
        query = "DELETE FROM album_songs WHERE album_id = %s AND song_id = %s"
        cursor.execute(query, (album_id, song_id))
        self.db_connector.connection.commit()
        print(f"Removed song {song_id} from album {album_id}")