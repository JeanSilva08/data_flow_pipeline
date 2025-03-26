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
        if not video_id or len(video_id) != 11:  # Standard YouTube ID length
            logger.warning(f"Invalid video ID: {video_id}")
            return 0
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
            if not self.db.is_connected():
                self.db.connect()

            # Fetch all songs with valid YouTube IDs
            songs = self.db.fetch_all(
                "SELECT song_id, youtube_id, main_artist_id FROM songs WHERE youtube_id IS NOT NULL AND youtube_id != ''"
            )
            if not songs:
                logger.warning("No songs found with valid YouTube IDs.")
                return

            # Track total views per artist for media kit
            artist_views = {}

            # Update views for each song
            for song in songs:
                song_id = song['song_id']
                youtube_id = song['youtube_id']
                artist_id = song['main_artist_id']

                try:
                    if not youtube_id or len(youtube_id) != 11:  # Standard YouTube ID length
                        logger.warning(f"Invalid video ID for song {song_id}: {youtube_id}")
                        continue

                    views = self.get_video_views(youtube_id)
                    if views > 0:  # Only update if we got valid views
                        self._save_youtube_views(song_id, artist_id, views)
                        logger.info(f"Updated YouTube views for song ID {song_id}: {views} views")

                        # Update artist total
                        artist_views[artist_id] = artist_views.get(artist_id, 0) + views
                except Exception as e:
                    logger.error(f"Error processing song ID {song_id}: {e}")
                    continue

            # Update media kit data with total YouTube views per artist
            self._update_media_kit_views(artist_views)

        except Exception as e:
            logger.error(f"Error updating YouTube views: {e}")
            raise

    def _update_media_kit_views(self, artist_views):
        """Update media_kit_data with total YouTube views per artist"""
        if not artist_views:
            return

        connection = self.db.connect()
        cursor = connection.cursor()
        try:
            for artist_id, total_views in artist_views.items():
                cursor.execute("""
                    INSERT INTO media_kit_data (artist_id, youtube_views)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE youtube_views = %s
                """, (artist_id, total_views, total_views))
            connection.commit()
            logger.info("Updated media_kit_data with YouTube view totals")
        except Exception as e:
            logger.error(f"Error updating media kit data: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

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

