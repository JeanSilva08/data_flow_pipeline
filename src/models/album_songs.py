class AlbumSongs:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def add_song_to_album(db, album_id, song_id):
        query = "INSERT INTO album_songs (album_id, song_id) VALUES (%s, %s)"
        db.execute_query(query, (album_id, song_id))

    def get_songs_by_album(self, album_id):
        """
        Retrieves all songs associated with a specific album.
        """
        cursor = self.db.connection.cursor(dictionary=True)
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
        cursor = self.db.connection.cursor()
        query = """
            SELECT albums.* FROM albums
            JOIN album_songs ON albums.album_id = album_songs.album_id
            WHERE album_songs.song_id = %s
        """
        cursor.execute(query, (song_id,))
        return cursor.fetchall()

    def remove_song_from_album(self, album_id, song_id):
        """
        Removes a relationship between an album and a song.
        """
        cursor = self.db.connection.cursor()
        query = "DELETE FROM album_songs WHERE album_id = %s AND song_id = %s"
        cursor.execute(query, (album_id, song_id))
        self.db.connection.commit()
        print(f"Removed song {song_id} from album {album_id}")

    @staticmethod
    def check_song_in_album(db, album_id, song_id):
        query = "SELECT * FROM album_songs WHERE album_id = %s AND song_id = %s"
        result = db.execute_query(query, (album_id, song_id))
        return bool(result)



    @staticmethod
    def get_all_album_song_relationships(db):
        """
        Retrieves all album-song relationships.
        """
        cursor = db.connection.cursor()
        query = "SELECT * FROM album_songs"
        cursor.execute(query)
        return cursor.fetchall()