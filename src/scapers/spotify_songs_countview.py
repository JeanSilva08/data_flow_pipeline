import logging
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class SpotifySongsCountView:
    def __init__(self, db_connector, batch_size=3, max_retries=20):
        self.db_connector = db_connector
        self.batch_size = batch_size  # Number of tabs to open at a time
        self.max_retries = max_retries  # Max retries for fetching play counts
        self.driver = self._setup_driver()
        self.logger = self._setup_logger()

    @staticmethod
    def _setup_driver():
        """Set up and return a headless Chrome WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(executable_path='/usr/bin/chromedriver')
        return webdriver.Chrome(service=service, options=chrome_options)

    @staticmethod
    def _setup_logger():
        """Set up and return a logger."""
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logger

    def _fetch_countview_from_url(self, url):
        """Fetch the play count from a single Spotify song URL."""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'title')))
            play_count_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="playcount"]'))
            )
            play_count_text = play_count_element.text
            play_count_digits = re.findall(r'\d+', play_count_text)
            play_count = int(''.join(play_count_digits))
            self.logger.info(f"Fetched {play_count} streams from {url}")
            return play_count
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            self.logger.error(f"Error fetching play count from {url}: {e}")
            return None

    def _fetch_countviews_in_batch(self, urls):
        """Fetch play counts for a batch of Spotify song URLs."""
        countview_data = {}
        for url in urls:
            countview = self._fetch_countview_from_url(url)
            if countview is not None:
                countview_data[url] = countview
        return countview_data

    def _save_countview_to_db(self, song_id, artist_id, countview):
        """Save the play count to the database."""
        if isinstance(countview, int):
            connection = self.db_connector.connect()
            cursor = connection.cursor()
            try:
                query = """
                    INSERT INTO spotify_song_countview (song_id, artist_id, countview)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (song_id, artist_id, countview))
                connection.commit()
                self.logger.info(f"Saved {countview} streams for song ID {song_id}")
            except Exception as e:
                self.logger.error(f"Error saving countview for song ID {song_id}: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        else:
            self.logger.warning(f"Invalid countview data for song ID {song_id}: {countview}")

    def _update_media_kit_data(self, artist_id, total_countview):
        """Update the total play count for an artist in the media_kit_data table."""
        connection = self.db_connector.connect()
        cursor = connection.cursor()
        try:
            # Check if the artist already exists in media_kit_data
            cursor.execute("SELECT artist_id FROM media_kit_data WHERE artist_id = %s", (artist_id,))
            if cursor.fetchone():
                # Update existing record
                query = """
                    UPDATE media_kit_data
                    SET song_count = %s
                    WHERE artist_id = %s
                """
                cursor.execute(query, (total_countview, artist_id))
            else:
                # Insert new record
                query = """
                    INSERT INTO media_kit_data (artist_id, song_count)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (artist_id, total_countview))
            connection.commit()
            self.logger.info(f"Updated total countview for artist ID {artist_id} to {total_countview}")
        except Exception as e:
            self.logger.error(f"Error updating total countview for artist ID {artist_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def _get_songs_with_spotify_url(self):
        """Fetch all songs with a Spotify URL from the database."""
        connection = self.db_connector.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT s.song_id, s.spotify_url, s.main_artist_id
                FROM songs s
                WHERE s.spotify_url IS NOT NULL
            """)
            results = cursor.fetchall()
            return results if results else []
        except Exception as e:
            self.logger.error(f"Error fetching songs from the database: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def _get_all_artists(self):
        """Fetch all artists from the database."""
        connection = self.db_connector.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT artist_id FROM artists")
            results = cursor.fetchall()
            return [row[0] for row in results] if results else []
        except Exception as e:
            self.logger.error(f"Error fetching artists from the database: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def _calculate_total_countview_for_artist(self, artist_id):
        """Calculate the total countview for a specific artist."""
        connection = self.db_connector.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT SUM(countview)
                FROM spotify_song_countview
                WHERE artist_id = %s
            """, (artist_id,))
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except Exception as e:
            self.logger.error(f"Error calculating total countview for artist ID {artist_id}: {e}")
            return 0
        finally:
            cursor.close()
            connection.close()

    def update_all_songs_countview(self):
        """Update play counts for all songs in the database."""
        songs = self._get_songs_with_spotify_url()
        if not songs:
            self.logger.warning("No songs with Spotify URLs found in the database.")
            return

        artist_total_countviews = {}  # To store total play counts per artist

        for i in range(0, len(songs), self.batch_size):
            batch = songs[i:i + self.batch_size]
            song_ids = [song_id for song_id, _, _ in batch]
            song_urls = [spotify_url for _, spotify_url, _ in batch]
            artist_ids = [artist_id for _, _, artist_id in batch]

            retries = 0
            countview_data = {}
            while retries < self.max_retries:
                countview_data = self._fetch_countviews_in_batch(song_urls)
                if all(countview is not None for countview in countview_data.values()):
                    break
                retries += 1
                self.logger.warning(f"Retrying batch {i // self.batch_size + 1} (Attempt {retries}/{self.max_retries})")
                time.sleep(5)

            if retries == self.max_retries:
                self.logger.error(f"Skipping batch starting with URL: {song_urls[0]} after {self.max_retries} failed attempts.")
                continue

            for song_id, song_url, artist_id in zip(song_ids, song_urls, artist_ids):
                countview = countview_data.get(song_url)
                if countview is not None:
                    self._save_countview_to_db(song_id, artist_id, countview)
                    # Update the artist's total play count
                    if artist_id in artist_total_countviews:
                        artist_total_countviews[artist_id] += countview
                    else:
                        artist_total_countviews[artist_id] = countview

        # Update total play count for each artist in the media_kit_data table
        all_artists = self._get_all_artists()
        for artist_id in all_artists:
            total_countview = self._calculate_total_countview_for_artist(artist_id)
            self._update_media_kit_data(artist_id, total_countview)

        self.driver.quit()
        self.logger.info("Finished updating play counts for all songs.")