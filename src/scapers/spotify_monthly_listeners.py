import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MonthlyListeners:
    def __init__(self, db_connector, batch_size=2):
        self.db_connector = db_connector
        self.batch_size = batch_size  # Number of tabs to open at a time
        self.driver = self._setup_driver()
        self.logger = self._setup_logger()

    def _setup_driver(self):
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

    def _setup_logger(self):
        """Set up and return a logger."""
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        return logger

    def _fetch_listeners_from_url(self, spotify_url):
        """Fetch monthly listeners from a single Spotify URL."""
        try:
            self.driver.get(spotify_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span.Ydwa1P5GkCggtLlSvphs'))
            )
            listeners_span = self.driver.find_element(By.CSS_SELECTOR, 'span.Ydwa1P5GkCggtLlSvphs')
            listeners_text = listeners_span.text.strip()
            listeners = int(listeners_text.split()[0].replace('.', '').replace(' ', ''))
            self.logger.info(f"Fetched {listeners} listeners from {spotify_url}")
            return listeners
        except Exception as e:
            self.logger.error(f"Error fetching listeners from {spotify_url}: {e}")
            return None

    def _fetch_listeners_in_batch(self, artist_urls):
        """Fetch monthly listeners for a batch of Spotify URLs."""
        listeners_data = {}
        for spotify_url in artist_urls:
            listeners = self._fetch_listeners_from_url(spotify_url)
            listeners_data[spotify_url] = listeners
        return listeners_data

    def _save_listeners_to_db(self, artist_id, listeners):
        """Save monthly listeners to the database."""
        if isinstance(listeners, int):
            connection = self.db_connector.connect()
            cursor = connection.cursor()
            try:
                query = """
                    INSERT INTO monthly_listeners (artist_id, listeners)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (artist_id, listeners))
                connection.commit()
                self.logger.info(f"Saved {listeners} listeners for artist ID {artist_id}")
            except Exception as e:
                self.logger.error(f"Error saving listeners for artist ID {artist_id}: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        else:
            self.logger.warning(f"Invalid listeners data for artist ID {artist_id}: {listeners}")

    def _get_artists_with_spotify_id(self):
        """Fetch all artists with a Spotify ID from the database."""
        connection = self.db_connector.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT artist_id, spotify_id FROM artists WHERE spotify_id IS NOT NULL ORDER BY artist_id")
            return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Error fetching artists from the database: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def update_all_artists(self):
        """Update monthly listeners for all artists in the database."""
        artists = self._get_artists_with_spotify_id()
        if not artists:
            self.logger.warning("No artists with Spotify IDs found in the database.")
            return

        for i in range(0, len(artists), self.batch_size):
            batch = artists[i:i + self.batch_size]
            artist_ids = [artist_id for artist_id, _ in batch]
            artist_urls = [f"https://open.spotify.com/artist/{spotify_id}" for _, spotify_id in batch]

            listeners_data = self._fetch_listeners_in_batch(artist_urls)

            for artist_id, spotify_url in zip(artist_ids, artist_urls):
                listeners = listeners_data.get(spotify_url)
                if listeners is not None:
                    self._save_listeners_to_db(artist_id, listeners)

        self.driver.quit()
        self.logger.info("Finished updating monthly listeners for all artists.")