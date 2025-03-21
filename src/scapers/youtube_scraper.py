import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


class YouTubeScraper:
    def __init__(self, batch_size=3, max_retries=3):
        """
        Initialize the YouTubeScraper class.

        Args:
            batch_size (int): Number of URLs to process in a batch. Default is 3.
            max_retries (int): Maximum number of retries for failed fetches. Default is 3.
        """
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

    def _fetch_views_from_url(self, url, retries=0):
        """
        Fetch video views from a single YouTube URL.

        Args:
            url (str): YouTube video URL.
            retries (int): Current retry attempt.

        Returns:
            int: Number of views, or None if fetching fails after max retries.
        """
        try:
            self.driver.get(url)
            # Wait for the page to load and ensure the title is present
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'title')))

            # Locate the view count element using a flexible XPath
            views_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//span[@class="bold" and (contains(text(), "visualizações") or contains(text(), "views"))]'))
            )

            # Extract and clean the view count
            views_text = views_element.text.strip()
            self.logger.info(f"Raw views text: {views_text}")
            views_text = views_text.replace(" visualizações", "").replace(" views", "").replace(".", "").replace(",", "")
            self.logger.info(f"Cleaned views text: {views_text}")

            # Handle empty views_text
            if not views_text:
                self.logger.warning(f"Empty views text for URL: {url}")
                return None

            views = int(views_text)
            self.logger.info(f"Fetched {views} views from {url}")
            return views

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            if retries < self.max_retries:
                self.logger.warning(f"Retrying {url} (Attempt {retries + 1}/{self.max_retries})")
                time.sleep(5)  # Wait before retrying
                return self._fetch_views_from_url(url, retries + 1)
            else:
                self.logger.error(f"Failed to fetch views from {url} after {self.max_retries} retries: {e}")
                return None

    def _fetch_views_in_batch(self, urls):
        """
        Fetch views for a batch of YouTube URLs.

        Args:
            urls (list): List of YouTube URLs.

        Returns:
            dict: Dictionary mapping URLs to their views.
        """
        views_data = {}
        for url in urls:
            views = self._fetch_views_from_url(url)
            if views is not None:
                views_data[url] = views
        return views_data

    def _save_views_to_db(self, db, song_id, artist_id, views):
        """
        Save YouTube views to the database.

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
                    INSERT INTO youtube_song_countview (song_id, artist_id, countview)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(query, (song_id, artist_id, views))
                connection.commit()
                self.logger.info(f"Saved {views} views for song ID {song_id}")
            except Exception as e:
                self.logger.error(f"Error saving views for song ID {song_id}: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        else:
            self.logger.warning(f"Invalid views data for song ID {song_id}: {views}")

    def _update_media_kit_data(self, db, artist_id, total_views):
        """
        Update the total YouTube views for an artist in the media_kit_data table.

        Args:
            db: Database connector object.
            artist_id (int): Artist ID in the database.
            total_views (int): Total YouTube views for the artist.
        """
        connection = db.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO media_kit_data (artist_id, youtube_views)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE youtube_views = %s
            """, (artist_id, total_views, total_views))
            connection.commit()
            self.logger.info(f"Updated media_kit_data for artist ID {artist_id} with {total_views} views")
        except Exception as e:
            self.logger.error(f"Error updating media_kit_data for artist ID {artist_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def update_all_youtube_views(self, db):
        """
        Update YouTube views for all songs in the database.
        """
        songs = db.fetch_all("SELECT song_id, youtube_url, main_artist_id FROM songs WHERE youtube_url IS NOT NULL")
        if not songs:
            self.logger.warning("No songs with YouTube URLs found in the database.")
            return

        artist_total_views = {}  # To store total views per artist

        for i in range(0, len(songs), self.batch_size):
            batch = songs[i:i + self.batch_size]
            song_ids = [song_id for song_id, _, _ in batch]
            song_urls = [youtube_url for _, youtube_url, _ in batch]
            artist_ids = [artist_id for _, _, artist_id in batch]

            views_data = self._fetch_views_in_batch(song_urls)

            for song_id, song_url, artist_id in zip(song_ids, song_urls, artist_ids):
                views = views_data.get(song_url)
                if views is not None:
                    self._save_views_to_db(db, song_id, artist_id, views)
                    # Update the artist's total views
                    if artist_id in artist_total_views:
                        artist_total_views[artist_id] += views
                    else:
                        artist_total_views[artist_id] = views

        # Update media_kit_data with total YouTube views for each artist
        for artist_id, total_views in artist_total_views.items():
            self._update_media_kit_data(db, artist_id, total_views)

        self.driver.quit()
        self.logger.info("Finished updating YouTube views for all songs.")