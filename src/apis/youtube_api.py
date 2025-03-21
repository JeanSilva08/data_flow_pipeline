import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeAPI:
    def __init__(self, api_key, db):
        """
        Initialize the YouTube API client with the provided API key and database connection.

        Args:
            api_key (str): YouTube Data API key.
            db: Database connection object (e.g., DBConnector).
        """
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self.db = db

    def get_video_views(self, video_id):
        """
        Fetch the view count for a YouTube video using its video ID.

        Args:
            video_id (str): YouTube video ID.

        Returns:
            int: Number of views, or 0 if the video is not found or an error occurs.
        """
        try:
            request = self.youtube.videos().list(part="statistics", id=video_id)
            response = request.execute()
            if response['items']:
                return int(response['items'][0]['statistics']['viewCount'])
            return 0
        except HttpError as e:
            logger.error(f"Failed to fetch views for video {video_id}: {e}")
            return 0

    def update_all_youtube_views(self):
        """
        Update the YouTube views for all songs in the database.
        """
        try:
            # Fetch all songs with valid YouTube IDs
            songs = self.db.fetch_all("SELECT song_id, youtube_id, main_artist_id FROM songs WHERE youtube_id IS NOT NULL")
            if not songs:
                logger.warning("No songs found with valid YouTube IDs.")
                return

            # Update views for each song
            for song in songs:
                song_id, youtube_id, artist_id = song
                views = self.get_video_views(youtube_id)
                if views:
                    self._save_youtube_views(song_id, artist_id, views)
                    logger.info(f"Updated YouTube views for song ID {song_id}: {views} views")

        except Exception as e:
            logger.error(f"Error updating YouTube views: {e}")

    def _save_youtube_views(self, song_id, artist_id, views):
        """
        Save the YouTube views to the `youtube_song_countview` table.

        Args:
            song_id (int): ID of the song.
            artist_id (int): ID of the main artist.
            views (int): Number of views.
        """
        connection = self.db.connect()
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO youtube_song_countview (song_id, artist_id, countview)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE countview = %s
            """
            cursor.execute(query, (song_id, artist_id, views, views))
            connection.commit()
            logger.info(f"Saved YouTube views for song ID {song_id}.")
        except Exception as e:
            logger.error(f"Failed to save YouTube views for song ID {song_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()