from src.models.album import Album
from src.models.song import Song


class AlbumSongs:
    def __init__(self, db):
        self.db = db

    def add_song_to_album(self, album_id, song_id):
        """Add a song to an album with error handling"""
        try:
            if not Album.exists(self.db, album_id=album_id):
                print(f"Album {album_id} doesn't exist")
                return False

            if not Song.exists(self.db, song_id=song_id):
                print(f"Song {song_id} doesn't exist")
                return False

            if self.check_song_in_album(album_id, song_id):
                print(f"Song {song_id} already in album {album_id}")
                return False

            query = "INSERT INTO album_songs (album_id, song_id) VALUES (%s, %s)"
            self.db.execute_query(query, (album_id, song_id))
            print("Song added to album successfully!")
            return True
        except Exception as e:
            print(f"Error adding song to album: {e}")
            return False

    def get_songs_by_album(self, album_id):
        """Get all songs in an album with proper error handling"""
        try:
            if not Album.exists(self.db, album_id=album_id):
                print(f"Album {album_id} doesn't exist")
                return []

            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT songs.* FROM songs
                JOIN album_songs ON songs.song_id = album_songs.song_id
                WHERE album_songs.album_id = %s
            """
            cursor.execute(query, (album_id,))
            return [Song(**row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching songs by album: {e}")
            return []

    def get_albums_for_song(self, song_id):
        """Get all albums containing a specific song"""
        try:
            if not Song.exists(self.db, song_id=song_id):
                print(f"Song {song_id} doesn't exist")
                return []

            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT albums.* FROM albums
                JOIN album_songs ON albums.album_id = album_songs.album_id
                WHERE album_songs.song_id = %s
            """
            cursor.execute(query, (song_id,))
            return [Album(**row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching albums for song: {e}")
            return []

    def remove_song_from_album(self, album_id, song_id):
        """Remove a song from an album"""
        try:
            if not self.check_song_in_album(album_id, song_id):
                print(f"Song {song_id} not in album {album_id}")
                return False

            query = "DELETE FROM album_songs WHERE album_id = %s AND song_id = %s"
            self.db.execute_query(query, (album_id, song_id))
            return True
        except Exception as e:
            print(f"Error removing song from album: {e}")
            return False

    def check_song_in_album(self, album_id, song_id):
        """Check if a song exists in an album"""
        try:
            cursor = self.db.connection.cursor()
            query = "SELECT 1 FROM album_songs WHERE album_id = %s AND song_id = %s"
            cursor.execute(query, (album_id, song_id))
            return bool(cursor.fetchone())
        except Exception as e:
            print(f"Error checking song in album: {e}")
            return False

    def get_all_album_song_relationships(self):
        """Get all album-song relationships"""
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            query = "SELECT * FROM album_songs"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching album-song relationships: {e}")
            return []