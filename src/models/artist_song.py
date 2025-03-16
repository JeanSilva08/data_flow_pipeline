from src.models.song import Song


class ArtistSongs:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def add_song_for_artist(db, artist_id, song_id):
        try:
            query = "INSERT INTO artist_songs (artist_id, song_id) VALUES (%s, %s)"
            db.execute_query(query, (artist_id, song_id))
            print("Song added for artist successfully!")
        except Exception as e:
            print(f"Error adding song for artist: {e}")

    def get_songs_by_artist(self, artist_id):
        cursor = self.db.connection.cursor(dictionary=True)
        query = """
            SELECT songs.* FROM songs
            JOIN artist_songs ON songs.song_id = artist_songs.song_id
            WHERE artist_songs.artist_id = %s
        """
        cursor.execute(query, (artist_id,))
        return [Song(**row) for row in cursor.fetchall()]

    def get_artists_for_song(self, song_id):
        cursor = self.db.connection.cursor(dictionary=True)
        query = """
            SELECT artists.* FROM artists
            JOIN artist_songs ON artists.artist_id = artist_songs.artist_id
            WHERE artist_songs.song_id = %s
        """
        cursor.execute(query, (song_id,))
        return cursor.fetchall()

    def remove_song_from_artist(self, artist_id, song_id):
        try:
            query = "DELETE FROM artist_songs WHERE artist_id = %s AND song_id = %s"
            self.db.execute_query(query, (artist_id, song_id))
            print(f"Removed song {song_id} from artist {artist_id}")
        except Exception as e:
            print(f"Error removing song from artist: {e}")

    @staticmethod
    def get_all_artist_song_relationships(db):
        """
        Retrieves all artist-song relationships.
        """
        cursor = db.connection.cursor()
        query = "SELECT * FROM song_artists"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def check_song_for_artist(db, artist_id, song_id):
        cursor = db.connection.cursor()
        query = "SELECT * FROM artist_songs WHERE artist_id = %s AND song_id = %s"
        cursor.execute(query, (artist_id, song_id))
        return bool(cursor.fetchone())