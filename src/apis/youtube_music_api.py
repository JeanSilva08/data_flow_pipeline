# In youtube_music_api.py
import logging
from googleapiclient.errors import HttpError
from src.apis.youtube_api import YouTubeAPI

logger = logging.getLogger(__name__)

class YouTubeMusicAPI(YouTubeAPI):
    def update_all_youtubemsc_views(self):
        try:
            if not self.db.is_connected():
                self.db.connect()

            songs = self.db.fetch_all(
                "SELECT song_id, ytmsc_id, main_artist_id FROM songs WHERE ytmsc_id IS NOT NULL AND ytmsc_id != ''"
            )
            if not songs:
                logger.warning("No songs found with valid YouTube Music IDs.")
                return

            for song in songs:
                song_id = song['song_id']
                ytmsc_id = song['ytmsc_id']
                artist_id = song['main_artist_id']

                try:
                    if not ytmsc_id or len(ytmsc_id) != 11:
                        logger.warning(f"Invalid video ID for song {song_id}: {ytmsc_id}")
                        continue

                    views = self.get_video_views(ytmsc_id)
                    if views > 0:
                        self.save_youtubemsc_views_to_db(song_id, artist_id, views)
                        logger.info(f"Updated YouTube Music views for song ID {song_id}: {views} views")
                except Exception as e:
                    logger.error(f"Error processing song ID {song_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error updating YouTube Music views: {e}")
            raise

    def save_youtubemsc_views_to_db(self, song_id, artist_id, views):
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