import json
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)


class Song:
    def __init__(self, **kwargs):
        self.song_id = kwargs.get("song_id")  # Add this line
        self.name = kwargs.get("name")
        self.main_artist_id = kwargs.get("main_artist_id")
        self.producer = kwargs.get("producer")
        self.record_label = kwargs.get("record_label")
        self.type = kwargs.get("type")
        self.release_date = kwargs.get("release_date")
        self.days_from_release = kwargs.get("days_from_release")
        self.spotify_id = kwargs.get("spotify_id")
        self.youtube_id = kwargs.get("youtube_id")
        self.ytmsc_id = kwargs.get("ytmsc_id")
        self.spotify_url = kwargs.get("spotify_url")
        self.youtube_url = kwargs.get("youtube_url")
        self.youtube_music_url = kwargs.get("youtube_music_url")
        self.album_id = kwargs.get("album_id")

        # Handle featured_artists - can be JSON string or list
        featured = kwargs.get("featured_artists", [])
        if isinstance(featured, str):
            try:
                self.featured_artists = json.loads(featured)
            except json.JSONDecodeError:
                self.featured_artists = []
        else:
            self.featured_artists = featured or []

    def save_to_db(self, db):
        """Save the song to the database and update the song_id"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor()
            query = """
                INSERT INTO songs (
                    name, main_artist_id, producer, record_label, type, release_date, 
                    days_from_release, spotify_id, youtube_id, ytmsc_id, spotify_url, 
                    youtube_url, youtube_music_url, album_id, featured_artists
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Convert release_date to proper format
            release_date = None
            if self.release_date:
                try:
                    if isinstance(self.release_date, str):
                        release_date = datetime.strptime(self.release_date, "%d-%m-%Y").date()
                    else:
                        release_date = self.release_date
                except ValueError:
                    logger.warning("Invalid release_date format. Setting to None")
                    release_date = None

            values = (
                self.name,
                self.main_artist_id,
                self.producer,
                self.record_label,
                self.type,
                release_date,
                self.days_from_release,
                self.spotify_id,
                self.youtube_id,
                self.ytmsc_id,
                self.spotify_url,
                self.youtube_url,
                self.youtube_music_url,
                self.album_id,
                json.dumps(self.featured_artists) if self.featured_artists else None
            )

            cursor.execute(query, values)
            self.song_id = cursor.lastrowid
            db.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving song to database: {e}")
            if db.connection:
                db.connection.rollback()
            return False

    @staticmethod
    def update_in_db(db, song_id, **kwargs):
        """Update song information in the database"""
        try:
            if not db.is_connected():
                db.connect()

            # Handle featured_artists conversion if present
            if 'featured_artists' in kwargs:
                featured = kwargs['featured_artists']
                if isinstance(featured, str):
                    try:
                        kwargs['featured_artists'] = json.loads(featured)
                    except json.JSONDecodeError:
                        kwargs['featured_artists'] = []
                kwargs['featured_artists'] = json.dumps(kwargs['featured_artists']) if kwargs[
                    'featured_artists'] else None

            # Handle release_date conversion if present
            if 'release_date' in kwargs and kwargs['release_date']:
                try:
                    if isinstance(kwargs['release_date'], str):
                        kwargs['release_date'] = datetime.strptime(kwargs['release_date'], "%d-%m-%Y").date()
                except ValueError:
                    logger.warning("Invalid release_date format. Setting to None")
                    kwargs['release_date'] = None

            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(song_id)

            query = f"""
                UPDATE songs
                SET {set_clause}
                WHERE song_id = %s
            """
            db.execute_query(query, values)
            return True
        except Exception as e:
            logger.error(f"Error updating song: {e}")
            return False

    @staticmethod
    def delete_from_db(db, song_id):
        """Delete a song from the database"""
        try:
            if not db.is_connected():
                db.connect()

            query = "DELETE FROM songs WHERE song_id = %s"
            db.execute_query(query, (song_id,))
            return True
        except Exception as e:
            logger.error(f"Error deleting song: {e}")
            return False

    @staticmethod
    def get_by_id(db, song_id):
        """Fetch a song by its ID"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM songs WHERE song_id = %s"
            cursor.execute(query, (song_id,))
            result = cursor.fetchone()
            return Song(**result) if result else None
        except Exception as e:
            logger.error(f"Error fetching song by ID: {e}")
            return None

    @staticmethod
    def get_by_spotify_id(db, spotify_id):
        """Fetch a song by its Spotify ID"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM songs WHERE spotify_id = %s"
            cursor.execute(query, (spotify_id,))
            result = cursor.fetchone()
            return Song(**result) if result else None
        except Exception as e:
            logger.error(f"Error fetching song by Spotify ID: {e}")
            return None

    @staticmethod
    def get_by_youtube_id(db, youtube_id):
        """Fetch a song by its YouTube ID"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM songs WHERE youtube_id = %s"
            cursor.execute(query, (youtube_id,))
            result = cursor.fetchone()
            return Song(**result) if result else None
        except Exception as e:
            logger.error(f"Error fetching song by YouTube ID: {e}")
            return None

    @staticmethod
    def get_all(db, limit=None):
        """Get all songs with optional limit"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM songs"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            return [Song(**row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching all songs: {e}")
            return []

    @staticmethod
    def get_by_artist(db, artist_id):
        """Get all songs by a specific artist"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor(dictionary=True)
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

    @staticmethod
    def get_by_album(db, album_id):
        """Get all songs in an album"""
        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM songs WHERE album_id = %s"
            cursor.execute(query, (album_id,))
            return [Song(**row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching songs by album: {e}")
            return []

    @staticmethod
    def exists(db, song_id=None, spotify_id=None, youtube_id=None):
        """Check if a song exists by ID, Spotify ID, or YouTube ID"""
        if not any([song_id, spotify_id, youtube_id]):
            return False

        try:
            if not db.is_connected():
                db.connect()

            cursor = db.connection.cursor()
            if song_id:
                query = "SELECT 1 FROM songs WHERE song_id = %s"
                cursor.execute(query, (song_id,))
            elif spotify_id:
                query = "SELECT 1 FROM songs WHERE spotify_id = %s"
                cursor.execute(query, (spotify_id,))
            else:
                query = "SELECT 1 FROM songs WHERE youtube_id = %s"
                cursor.execute(query, (youtube_id,))
            return bool(cursor.fetchone())
        except Exception as e:
            logger.error(f"Error checking song existence: {e}")
            return False