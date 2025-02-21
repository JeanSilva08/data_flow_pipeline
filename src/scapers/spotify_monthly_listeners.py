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
        self.batch_size = batch_size  # Adjustable number of tabs to open at a time
        self.driver = self.setup_driver()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)  # Configure logging

    @staticmethod
    def setup_driver():
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(executable_path='/usr/bin/chromedriver')
        return webdriver.Chrome(service=service, options=chrome_options)

    def fetch_listeners_from_tabs(self, artist_urls):
        listeners_data = {}
        tabs = []

        # Open the initial tabs
        for spotify_url in artist_urls:
            self.driver.execute_script("window.open('');")  # Open a new tab
            tabs.append(self.driver.window_handles[-1])  # Add the tab to the list
            self.driver.switch_to.window(tabs[-1])  # Switch to the new tab
            self.driver.get(spotify_url)  # Load the page

            # Wait for the listener count to be visible
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span.Ydwa1P5GkCggtLlSvphs'))
                )
            except Exception as e:
                self.logger.error(f"Error loading {spotify_url}: {str(e)}")
                listeners_data[spotify_url] = None
                continue

        # Fetch listeners data
        for tab, spotify_url in zip(tabs, artist_urls):
            self.driver.switch_to.window(tab)  # Switch to the tab
            try:
                listeners_span = self.driver.find_element(By.CSS_SELECTOR, 'span.Ydwa1P5GkCggtLlSvphs')
                listeners_text = listeners_span.text.strip()
                self.logger.info(f"Found listeners text: {listeners_text} from {spotify_url}")

                listeners = int(listeners_text.split()[0].replace('.', '').replace(' ', ''))
                listeners_data[spotify_url] = listeners
            except Exception as e:
                self.logger.error(f"Problem fetching data for {spotify_url}: {str(e)}")
                listeners_data[spotify_url] = None

        # Close all tabs except the first one
        for tab in tabs:
            self.driver.switch_to.window(tab)
            self.driver.close()

        self.driver.switch_to.window(self.driver.window_handles[0])  # Switch back to the first tab
        return listeners_data

    def save_to_db(self, artist_id, listeners):
        if isinstance(listeners, int):
            connection = self.db_connector.connect()  # Ensure a fresh connection
            cursor = connection.cursor()

            try:
                query = """
                    INSERT INTO monthly_listeners (artist_id, listeners)
                    VALUES (%s, %s)
                """
                cursor.execute(query, (artist_id, listeners))
                connection.commit()
                self.logger.info(f"Inserted {listeners} listeners for artist with ID {artist_id}")
            except Exception as e:
                self.logger.error(f"Error inserting data: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        else:
            self.logger.warning(f"Invalid data type for listeners: {listeners}, expected int")

    def update_all_artists(self):
        connection = self.db_connector.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT artist_id, spotify_id FROM artists WHERE spotify_id IS NOT NULL ORDER BY artist_id")
        artists = cursor.fetchall()

        # Process artists in batches
        for i in range(0, len(artists), self.batch_size):
            batch = artists[i:i + self.batch_size]  # Get the next batch
            artist_ids = [artist_id for artist_id, _ in batch]
            artist_urls = [f"https://open.spotify.com/artist/{spotify_id}" for _, spotify_id in batch]

            listeners_data = self.fetch_listeners_from_tabs(artist_urls)

            # Save fetched data to the database
            for artist_id, spotify_url in zip(artist_ids, artist_urls):
                listeners = listeners_data.get(spotify_url)
                if listeners is not None:
                    self.save_to_db(artist_id, listeners)

        cursor.close()
        self.driver.quit()
