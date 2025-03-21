import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Import YouTubeScraper from the correct module
from src.scapers.youtube_scraper import YouTubeScraper

class YouTubeMusicScraper(YouTubeScraper):
    def update_all_youtubemsc_views(self, db):
        """
        Update YouTube Music views for all songs in the database.
        """
        songs = db.fetch_all("SELECT song_id, youtube_music_url, main_artist_id FROM songs WHERE youtube_music_url IS NOT NULL")
        if not songs:
            self.logger.warning("No songs with YouTube Music URLs found in the database.")
            return

        artist_total_views = {}  # To store total views per artist

        for i in range(0, len(songs), self.batch_size):
            batch = songs[i:i + self.batch_size]
            song_ids = [song_id for song_id, _, _ in batch]
            song_urls = [youtube_music_url for _, youtube_music_url, _ in batch]
            artist_ids = [artist_id for _, _, artist_id in batch]

            views_data = self._fetch_views_in_batch(song_urls)

            for song_id, song_url, artist_id in zip(song_ids, song_urls, artist_ids):
                views = views_data.get(song_url)
                if views is not None:
                    self._save_youtubemsc_views_to_db(db, song_id, artist_id, views)
                    # Update the artist's total views
                    if artist_id in artist_total_views:
                        artist_total_views[artist_id] += views
                    else:
                        artist_total_views[artist_id] = views

        # Update media_kit_data with total YouTube Music views for each artist
        for artist_id, total_views in artist_total_views.items():
            self._update_media_kit_data(db, artist_id, total_views)

        self.driver.quit()
        self.logger.info("Finished updating YouTube Music views for all songs.")

    def _save_youtubemsc_views_to_db(self, db, song_id, artist_id, views):
        """
        Save YouTube Music views to the database.

        Args:
            db: Database connector object.
            song_id (int): Song ID in the database.
            artist_id (int): Artist ID in the database.
            views (int): Number of views.
        """
        if isinstance(views, int):
            connection = db.connect()
            cursor = connection.cursor()
            try:
                query = """
                    INSERT INTO youtubemsc_song_countview (song_id, artist_id, countview)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (song_id, artist_id, views))
                connection.commit()
                self.logger.info(f"Saved {views} YouTube Music views for song ID {song_id}")
            except Exception as e:
                self.logger.error(f"Error saving YouTube Music views for song ID {song_id}: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        else:
            self.logger.warning(f"Invalid YouTube Music views data for song ID {song_id}: {views}")

    def _update_media_kit_data(self, db, artist_id, total_views):
        """
        Update the total YouTube Music views for an artist in the media_kit_data table.

        Args:
            db: Database connector object.
            artist_id (int): Artist ID in the database.
            total_views (int): Total YouTube Music views for the artist.
        """
        connection = db.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO media_kit_data (artist_id, youtube_music_views)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE youtube_music_views = %s
            """, (artist_id, total_views, total_views))
            connection.commit()
            self.logger.info(f"Updated media_kit_data for artist ID {artist_id} with {total_views} YouTube Music views")
        except Exception as e:
            self.logger.error(f"Error updating media_kit_data for artist ID {artist_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()