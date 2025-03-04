import logging
from src.database.db_connector import DBConnector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DBSetup:
    def __init__(self, db_connector):
        """
        Initialize the DBSetup with a DBConnector instance.
        """
        self.db = db_connector

    def create_tables(self):
        """
        Create all necessary tables in the database.
        """
        try:
            # Artists table
            self._create_artists_table()

            # Songs table
            self._create_songs_table()

            # Albums table
            self._create_albums_table()

            # Playlists table
            self._create_playlists_table()

            # AlbumSongs table (many-to-many relationship between albums and songs)
            self._create_album_songs_table()

            # PlaylistSongs table (many-to-many relationship between playlists and songs)
            self._create_playlist_songs_table()

            # MonthlyListeners table
            self._create_monthly_listeners_table()

            # SpotifyArtistData table
            self._create_spotify_artist_data_table()

            logger.info("All tables created successfully.")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def _create_artists_table(self):
        """
        Create the 'artists' table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS artists (
                artist_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                r_label VARCHAR(100),
                spotify_id VARCHAR(100),
                youtube_id VARCHAR(100),
                Instagram_id VARCHAR(100),
                TikTok_id VARCHAR(100),
                Twitter_id VARCHAR(100),
                Twitch_id VARCHAR(100),
                Spotify_url VARCHAR(255),
                youtube_url VARCHAR(255),
                instagram_url VARCHAR(255),
                tiktok_url VARCHAR(255),
                twitter_url VARCHAR(255),
                twitch_url VARCHAR(255)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'artists' table.")

    def _create_songs_table(self):
        """
        Create the 'songs' table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS songs (
                song_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                main_artist_id INT,
                producer VARCHAR(100),
                ytmsc_id VARCHAR(100),
                record_label VARCHAR(100),
                type VARCHAR(50),
                release_date DATE,
                days_from_release INT,
                spotify_id VARCHAR(100),
                youtube_id VARCHAR(100),
                spotify_url VARCHAR(255),
                youtube_url VARCHAR(255),
                youtube_music_url VARCHAR(255),
                album_id INT,
                featured_artists JSON,
                FOREIGN KEY (main_artist_id) REFERENCES artists(artist_id),
                FOREIGN KEY (album_id) REFERENCES albums(album_id)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'songs' table.")

    def _create_albums_table(self):
        """
        Create the 'albums' table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS albums (
                album_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                artist_id INT,
                number_related_on_release_position INT,
                spotify_album_id VARCHAR(100),
                spotify_url VARCHAR(255),
                youtube_id VARCHAR(100),
                youtube_url VARCHAR(255),
                youtube_music_id VARCHAR(100),
                youtube_music_url VARCHAR(255),
                FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'albums' table.")

    def _create_playlists_table(self):
        """
        Create the 'playlists' table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS playlists (
                playlist_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                spotify_playlist_id VARCHAR(100),
                spotify_url VARCHAR(255)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'playlists' table.")

    def _create_album_songs_table(self):
        """
        Create the 'album_songs' table (many-to-many relationship between albums and songs).
        """
        query = """
            CREATE TABLE IF NOT EXISTS album_songs (
                album_id INT,
                song_id INT,
                PRIMARY KEY (album_id, song_id),
                FOREIGN KEY (album_id) REFERENCES albums(album_id),
                FOREIGN KEY (song_id) REFERENCES songs(song_id)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'album_songs' table.")

    def _create_playlist_songs_table(self):
        """
        Create the 'playlist_songs' table (many-to-many relationship between playlists and songs).
        """
        query = """
            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INT,
                song_id INT,
                PRIMARY KEY (playlist_id, song_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id),
                FOREIGN KEY (song_id) REFERENCES songs(song_id)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'playlist_songs' table.")

    def _create_monthly_listeners_table(self):
        """
        Create the 'monthly_listeners' table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS monthly_listeners (
                listener_id INT AUTO_INCREMENT PRIMARY KEY,
                artist_id INT,
                listeners INT,
                timestamp DATETIME,
                FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'monthly_listeners' table.")

    def _create_spotify_artist_data_table(self):
        """
        Create the 'spotify_artist_data' table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS spotify_artist_data (
                data_id INT AUTO_INCREMENT PRIMARY KEY,
                artist_id INT,
                song_count INT,
                followers INT,
                timestamp DATETIME,
                FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
            )
        """
        self.db.execute_query(query)
        logger.info("Created 'spotify_artist_data' table.")


if __name__ == "__main__":
    # Initialize the database connector
    db = DBConnector(
        host='your_db_host',
        database='your_db_name',
        user='your_db_user',
        password='your_db_password'
    )
    db.connect()

    # Initialize the DBSetup
    db_setup = DBSetup(db)

    # Create tables
    db_setup.create_tables()

    # Close the database connection
    db.close()