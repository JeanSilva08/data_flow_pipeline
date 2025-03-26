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
        """
        Initialize the SpotifySongsCountView class.

        Args:
            db_connector: Database connector object.
            batch_size (int): Number of URLs to process in a batch. Default is 3.
            max_retries (int): Maximum number of retries for failed fetches. Default is 3.
        """
        self.db_connector = db_connector
        self.batch_size = batch_size
        self.max_retries = max_retries
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

    def _fetch_countview_from_url(self, url, retries=0):
        """
        Fetch the play count from a single Spotify song URL.

        Args:
            url (str): Spotify song URL.
            retries (int): Current retry attempt.

        Returns:
            int: Play count, or None if fetching fails after max retries.
        """
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
            if retries < self.max_retries:
                self.logger.warning(f"Retrying {url} (Attempt {retries + 1}/{self.max_retries})")
                time.sleep(5)  # Wait before retrying
                return self._fetch_countview_from_url(url, retries + 1)
            else:
                self.logger.error(f"Failed to fetch play count from {url} after {self.max_retries} retries: {e}")
                return None

    def _fetch_countviews_in_batch(self, urls):
        """
        Fetch play counts for a batch of Spotify song URLs.

        Args:
            urls (list): List of Spotify song URLs.

        Returns:
            dict: Dictionary mapping URLs to their play counts.
        """
        countview_data = {}
        for url in urls:
            countview = self._fetch_countview_from_url(url)
            if countview is not None:
                countview_data[url] = countview
        return countview_data

    def _save_countview_to_db(self, song_id, artist_id, countview):
        """
        Save the play count to the database with song and album info.
        """
        if isinstance(countview, int):
            connection = self.db_connector.connect()
            cursor = connection.cursor()
            try:
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
                    INSERT INTO spotify_song_countview 
                    (song_id, artist_id, countview, song_name, album_name, album_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (song_id, artist_id, countview, song_name, album_name, album_id))
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

    def _get_songs_with_spotify_url(self):
        """
        Fetch all songs with a Spotify URL from the database.

        Returns:
            list: List of tuples containing song_id, spotify_url, and artist_id.
        """
        connection = self.db_connector.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT s.song_id, s.spotify_url, s.main_artist_id
                FROM songs s
                WHERE s.spotify_url IS NOT NULL
            """)
            return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Error fetching songs from the database: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def update_all_songs_countview(self):
        """
        Update play counts for all songs in the database.
        """
        songs = self._get_songs_with_spotify_url()
        if not songs:
            self.logger.warning("No songs with Spotify URLs found in the database.")
            return

        for i in range(0, len(songs), self.batch_size):
            batch = songs[i:i + self.batch_size]
            song_ids = [song_id for song_id, _, _ in batch]
            song_urls = [spotify_url for _, spotify_url, _ in batch]
            artist_ids = [artist_id for _, _, artist_id in batch]

            countview_data = self._fetch_countviews_in_batch(song_urls)

            for song_id, song_url, artist_id in zip(song_ids, song_urls, artist_ids):
                countview = countview_data.get(song_url)
                if countview is not None:
                    self._save_countview_to_db(song_id, artist_id, countview)

        self.driver.quit()
        self.logger.info("Finished updating play counts for all songs.")

