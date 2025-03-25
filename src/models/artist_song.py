from src.models.song import Song


class ArtistSongs:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def add_song_for_artist(db, artist_id, song_id):
        """Add a song-artist relationship"""
        try:
            if not db.is_connected():
                db.connect()

            # Check if relationship already exists
            if ArtistSongs.check_song_for_artist(db, artist_id, song_id):
                logger.warning(f"Song {song_id} already associated with artist {artist_id}")
                return False

            query = "INSERT INTO song_artists (artist_id, song_id) VALUES (%s, %s)"
            db.execute_query(query, (artist_id, song_id))
            return True
        except Exception as e:
            logger.error(f"Error adding song for artist: {e}")
            return False

    def get_songs_by_artist(self, artist_id):
        """Get all songs by a specific artist"""
        try:
            if not self.db.is_connected():
                self.db.connect()

            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT s.* FROM songs s
                JOIN song_artists sa ON s.song_id = sa.song_id
                WHERE sa.artist_id = %s
            """
            cursor.execute(query, (artist_id,))
            return [Song(**row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching songs by artist: {e}")
            return []

    def get_artists_for_song(self, song_id):
        """Get all artists for a specific song"""
        try:
            if not self.db.is_connected():
                self.db.connect()

            cursor = self.db.connection.cursor(dictionary=True)
            query = """
                SELECT a.* FROM artists a
                JOIN song_artists sa ON a.artist_id = sa.artist_id
                WHERE sa.song_id = %s
            """
            cursor.execute(query, (song_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching artists for song: {e}")
            return []

    def remove_song_from_artist(self, artist_id, song_id):
        """Remove a song-artist relationship"""
        try:
            if not self.db.is_connected():
                self.db.connect()

            query = "DELETE FROM song_artists WHERE artist_id = %s AND song_id = %s"
            self.db.execute_query(query, (artist_id, song_id))
            return True
        except Exception as e:
            logger.error(f"Error removing song from artist: {e}")
            return False

    @staticmethod
    def get_all_artist_song_relationships(db):
        """Get all artist-song relationships"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM song_artists"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching artist-song relationships: {e}")
            return []

    @staticmethod
    def check_song_for_artist(db, artist_id, song_id):
        """Check if a song-artist relationship exists"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor()
            query = "SELECT 1 FROM song_artists WHERE artist_id = %s AND song_id = %s"
            cursor.execute(query, (artist_id, song_id))
            return bool(cursor.fetchone())
        except Exception as e:
            logger.error(f"Error checking song for artist: {e}")
            return False