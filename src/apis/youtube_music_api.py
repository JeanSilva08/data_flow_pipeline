import logging
from googleapiclient.errors import HttpError
from src.apis.youtube_api import YouTubeAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeMusicAPI(YouTubeAPI):
    def update_all_youtubemsc_views(self):
        """Update YouTube Music views for all songs"""
        try:
            # Ensure database connection
            if not self.db.is_connected():
                self.db.connect()

            # Fetch all songs with valid YouTube Music IDs
            songs = self.db.fetch_all(
                "SELECT song_id, ytmsc_id, main_artist_id FROM songs WHERE ytmsc_id IS NOT NULL AND ytmsc_id != ''"
            )
            if not songs:
                logger.warning("No songs found with valid YouTube Music IDs.")
                return

            # Track total views per artist for media kit
            artist_views = {}

            for song in songs:
                song_id = song['song_id']
                ytmsc_id = song['ytmsc_id']
                artist_id = song['main_artist_id']

                try:
                    if not ytmsc_id or len(ytmsc_id) != 11:  # Standard YouTube ID length
                        logger.warning(f"Invalid video ID for song {song_id}: {ytmsc_id}")
                        continue

                    views = self.get_video_views(ytmsc_id)
                    if views > 0:  # Only update if we got valid views
                        self.save_youtubemsc_views_to_db(song_id, artist_id, views)
                        logger.info(f"Updated YouTube Music views for song ID {song_id}: {views} views")

                        # Update artist total
                        artist_views[artist_id] = artist_views.get(artist_id, 0) + views
                except Exception as e:
                    logger.error(f"Error processing song ID {song_id}: {e}")
                    continue

            # Update media kit data with totals
            self._update_media_kit_views(artist_views)

        except Exception as e:
            logger.error(f"Error updating YouTube Music views: {e}")
            raise

    def save_youtubemsc_views_to_db(self, song_id, artist_id, views):
        """
        Save the YouTube Music views to the database.
        """
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO youtubemsc_song_countview (song_id, artist_id, countview)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE countview = %s
            """
            cursor.execute(query, (song_id, artist_id, views, views))
            self.db.connection.commit()
            logger.info(f"Saved YouTube Music views for song ID {song_id}.")
        except Exception as e:
            logger.error(f"Error saving YouTube Music views for song ID {song_id}: {e}")
            self.db.connection.rollback()
        finally:
            if cursor:
                cursor.close()

    def _update_media_kit_views(self, artist_views):
        """Update media_kit_data with YouTube Music view totals"""
        if not artist_views:
            return

        cursor = None
        try:
            cursor = self.db.connection.cursor()
            for artist_id, total_views in artist_views.items():
                cursor.execute("""
                    INSERT INTO media_kit_data (artist_id, youtube_music_views)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE youtube_music_views = %s
                """, (artist_id, total_views, total_views))
            self.db.connection.commit()
            logger.info("Updated media_kit_data with YouTube Music view totals")
        except Exception as e:
            logger.error(f"Error updating media kit data: {e}")
            self.db.connection.rollback()
        finally:
            if cursor:
                cursor.close()