import logging
from datetime import datetime
from src.database.db_connector import DBConnector

logger = logging.getLogger(__name__)

class MediaKitTransformer:
    def __init__(self, db: DBConnector):
        self.db = db

    def _fetch_artist_data(self):
        """
        Fetch all artist data from the database.
        """
        query = """
            SELECT artist_id, name, category, r_label
            FROM artists
        """
        return self.db.fetch_all(query)

    def _fetch_spotify_data(self, artist_id):
        """
        Fetch Spotify data for a specific artist.
        """
        query = """
            SELECT followers, song_count
            FROM spotify_artist_data
            WHERE artist_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """
        return self.db.fetch_one(query, (artist_id,))

    def _fetch_monthly_listeners(self, artist_id):
        """
        Fetch monthly listeners for a specific artist.
        """
        query = """
            SELECT listeners
            FROM monthly_listeners
            WHERE artist_id = %s
            ORDER BY fetched_at DESC
            LIMIT 1
        """
        return self.db.fetch_one(query, (artist_id,))

    def _fetch_latest_youtube_views(self, artist_id):
        """
        Fetch latest YouTube views for a specific artist's songs.
        Only sums the most recent view count for each song.
        """
        query = """
            SELECT SUM(latest_views.countview) AS total_views
            FROM (
                SELECT ysc.song_id, ysc.countview
                FROM youtube_song_countview ysc
                INNER JOIN (
                    SELECT song_id, MAX(scraped_at) AS latest_scrape
                    FROM youtube_song_countview
                    WHERE artist_id = %s
                    GROUP BY song_id
                ) latest ON ysc.song_id = latest.song_id AND ysc.scraped_at = latest.latest_scrape
                WHERE ysc.artist_id = %s
            ) AS latest_views
        """
        return self.db.fetch_one(query, (artist_id, artist_id))

    def _fetch_latest_youtube_music_views(self, artist_id):
        """
        Fetch latest YouTube Music views for a specific artist's songs.
        Only sums the most recent view count for each song.
        """
        query = """
            SELECT SUM(latest_views.countview) AS total_views
            FROM (
                SELECT ymsc.song_id, ymsc.countview
                FROM youtubemsc_song_countview ymsc
                INNER JOIN (
                    SELECT song_id, MAX(scraped_at) AS latest_scrape
                    FROM youtubemsc_song_countview
                    WHERE artist_id = %s
                    GROUP BY song_id
                ) latest ON ymsc.song_id = latest.song_id AND ymsc.scraped_at = latest.latest_scrape
                WHERE ymsc.artist_id = %s
            ) AS latest_views
        """
        return self.db.fetch_one(query, (artist_id, artist_id))

    def _fetch_latest_spotify_streams(self, artist_id):
        """
        Fetch the sum of latest song streams for a specific artist from spotify_song_countview.
        Only sums the most recent stream count for each song.
        """
        query = """
            SELECT SUM(latest_views.countview) AS total_streams
            FROM (
                SELECT ssc.song_id, ssc.countview
                FROM spotify_song_countview ssc
                INNER JOIN (
                    SELECT song_id, MAX(scraped_at) AS latest_scrape
                    FROM spotify_song_countview
                    WHERE artist_id = %s
                    GROUP BY song_id
                ) latest ON ssc.song_id = latest.song_id AND ssc.scraped_at = latest.latest_scrape
                WHERE ssc.artist_id = %s
            ) AS latest_views
        """
        result = self.db.fetch_one(query, (artist_id, artist_id))
        return result["total_streams"] if result and result["total_streams"] else None

    def _fetch_artist_song_count(self, artist_id):
        """
        Fetch the count of songs registered for a specific artist in the songs table.
        """
        query = """
            SELECT COUNT(*) AS song_count
            FROM songs
            WHERE main_artist_id = %s
        """
        result = self.db.fetch_one(query, (artist_id,))
        return result["song_count"] if result else 0

    def transform_and_load(self):
        """
        Transform data from various tables and load it into media_kit_data.
        """
        artists = self._fetch_artist_data()
        for artist in artists:
            artist_id = artist["artist_id"]
            spotify_data = self._fetch_spotify_data(artist_id)
            monthly_listeners = self._fetch_monthly_listeners(artist_id)
            youtube_views = self._fetch_latest_youtube_views(artist_id)
            youtube_music_views = self._fetch_latest_youtube_music_views(artist_id)
            spotify_total_streams = self._fetch_latest_spotify_streams(artist_id)
            spotify_song_count = self._fetch_artist_song_count(artist_id)

            # Prepare data for media_kit_data
            media_kit_data = {
                "artist_id": artist_id,
                "artist_name": artist.get("name"),
                "category": artist.get("category"),
                "record_label": artist.get("r_label"),
                "spotify_song_count": spotify_song_count,  # Number of songs in database
                "spotify_total_streams": spotify_total_streams,  # Total streams from Spotify
                "spotify_monthly_listeners": monthly_listeners.get("listeners") if monthly_listeners else None,
                "spotify_followers": spotify_data.get("followers") if spotify_data else None,
                "youtube_views": youtube_views.get("total_views") if youtube_views else None,
                "youtube_music_views": youtube_music_views.get("total_views") if youtube_music_views else None,
            }

            # Insert or update media_kit_data
            self._update_media_kit_data(media_kit_data)

    def _update_media_kit_data(self, data):
        """
        Insert or update media_kit_data for an artist.
        """
        query = """
            INSERT INTO media_kit_data (
                artist_id, artist_name, category, record_label,
                spotify_song_count, spotify_total_streams,
                spotify_monthly_listeners, spotify_followers,
                youtube_views, youtube_music_views
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                artist_name = VALUES(artist_name),
                category = VALUES(category),
                record_label = VALUES(record_label),
                spotify_song_count = VALUES(spotify_song_count),
                spotify_total_streams = VALUES(spotify_total_streams),
                spotify_monthly_listeners = VALUES(spotify_monthly_listeners),
                spotify_followers = VALUES(spotify_followers),
                youtube_views = VALUES(youtube_views),
                youtube_music_views = VALUES(youtube_music_views)
        """
        values = (
            data["artist_id"], data["artist_name"], data["category"],
            data["record_label"], data["spotify_song_count"],
            data["spotify_total_streams"], data["spotify_monthly_listeners"],
            data["spotify_followers"], data["youtube_views"],
            data["youtube_music_views"]
        )
        self.db.execute_query(query, values)
        logger.info(f"Updated media_kit_data for artist ID {data['artist_id']}")