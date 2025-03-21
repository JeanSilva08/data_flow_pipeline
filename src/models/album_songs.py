from src.models.song import Song


class AlbumSongs:
    def __init__(self, db):
        self.db = db

    def add_song_to_album(self, album_id, song_id):
        """
        Add a song to an album.
        """
        try:
            query = "INSERT INTO album_songs (album_id, song_id) VALUES (%s, %s)"
            self.db.execute_query(query, (album_id, song_id))
            print("Song added to album successfully!")
        except Exception as e:
            print(f"Error adding song to album: {e}")

    def get_songs_by_album(self, album_id):
        """
        Get all songs in an album.
        """
        cursor = self.db.connection.cursor(dictionary=True)
        query = """
            SELECT songs.* FROM songs
            JOIN album_songs ON songs.song_id = album_songs.song_id
            WHERE album_songs.album_id = %s
        """
        cursor.execute(query, (album_id,))
        return [Song(**row) for row in cursor.fetchall()]

    def get_albums_for_song(self, song_id):
        """
        Get all albums that contain a specific song.
        """
        cursor = self.db.connection.cursor(dictionary=True)
        query = """
            SELECT albums.* FROM albums
            JOIN album_songs ON albums.album_id = album_songs.album_id
            WHERE album_songs.song_id = %s
        """
        cursor.execute(query, (song_id,))
        return cursor.fetchall()

    def remove_song_from_album(self, album_id, song_id):
        """
        Remove a song from an album.
        """
        try:
            query = "DELETE FROM album_songs WHERE album_id = %s AND song_id = %s"
            self.db.execute_query(query, (album_id, song_id))
            print(f"Removed song {song_id} from album {album_id}")
        except Exception as e:
            print(f"Error removing song from album: {e}")

    def check_song_in_album(self, album_id, song_id):
        """
        Check if a song is in an album.
        """
        cursor = self.db.connection.cursor()
        query = "SELECT * FROM album_songs WHERE album_id = %s AND song_id = %s"
        cursor.execute(query, (album_id, song_id))
        return bool(cursor.fetchone())

    def get_all_album_song_relationships(self):
        """
        Retrieve all album-song relationships.
        """
        cursor = self.db.connection.cursor()
        query = "SELECT * FROM album_songs"
        cursor.execute(query)
        return cursor.fetchall()