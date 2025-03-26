# In youtube_api.py
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class YouTubeAPI:
    def __init__(self, api_key, db):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self.db = db

    def get_video_views(self, video_id):
        if not video_id or len(video_id) != 11:
            logger.warning(f"Invalid video ID: {video_id}")
            return 0

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
        try:
            if not self.db.is_connected():
                self.db.connect()

            songs = self.db.fetch_all(
                "SELECT song_id, youtube_id, main_artist_id FROM songs WHERE youtube_id IS NOT NULL AND youtube_id != ''"
            )
            if not songs:
                logger.warning("No songs found with valid YouTube IDs.")
                return

            for song in songs:
                song_id = song['song_id']
                youtube_id = song['youtube_id']
                artist_id = song['main_artist_id']

                try:
                    if not youtube_id or len(youtube_id) != 11:
                        logger.warning(f"Invalid video ID for song {song_id}: {youtube_id}")
                        continue

                    views = self.get_video_views(youtube_id)
                    if views > 0:
                        self._save_youtube_views(song_id, artist_id, views)
                        logger.info(f"Updated YouTube views for song ID {song_id}: {views} views")
                except Exception as e:
                    logger.error(f"Error processing song ID {song_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error updating YouTube views: {e}")
            raise

    def _save_youtube_views(self, song_id, artist_id, views):
        cursor = None
        try:
            cursor = self.db.connection.cursor()
            # First get song and album info
            cursor.execute("""
                SELECT s.name, a.name, s.album_id 
                FROM songs s
                LEFT JOIN albums a ON s.album_id = a.album_id
                WHERE s.song_id = %s
            """, (song_id,))
            song_info = cursor.fetchone()

            song_name = song_info[0] if song_info else None
            album_name = song_info[1] if song_info else None
            album_id = song_info[2] if song_info else None

            query = """
                INSERT INTO youtube_song_countview 
                (song_id, artist_id, countview, song_name, album_name, album_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    countview = VALUES(countview),
                    song_name = VALUES(song_name),
                    album_name = VALUES(album_name),
                    album_id = VALUES(album_id)
            """
            cursor.execute(query, (song_id, artist_id, views, song_name, album_name, album_id))
            self.db.connection.commit()
            logger.info(f"Saved YouTube views for song ID {song_id}.")
        except Exception as e:
            logger.error(f"Failed to save YouTube views for song ID {song_id}: {e}")
            self.db.connection.rollback()
        finally:
            if cursor:
                cursor.close()

