from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class MonthlyListeners:
    def __init__(self, db_connector, batch_size=5):
        self.db_connector = db_connector
        self.batch_size = batch_size  # Adjustable number of tabs to open at a time
        self.driver = self.setup_driver()

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
        # Open multiple tabs and fetch listeners data
        listeners_data = {}
        tabs = []

        # Open the initial tab and store tabs references
        for spotify_url in artist_urls:
            self.driver.execute_script("window.open('');")  # Open a new tab
            tabs.append(self.driver.window_handles[-1])  # Add the tab to the list
            self.driver.switch_to.window(tabs[-1])  # Switch to the new tab
            self.driver.get(spotify_url)  # Load the page
            time.sleep(4)  # Wait for the page to load

        # Fetch listeners data from each tab
        for tab, spotify_url in zip(tabs, artist_urls):
            self.driver.switch_to.window(tab)  # Switch to the tab
            try:
                listeners_span = self.driver.find_element(By.CSS_SELECTOR, 'span.Ydwa1P5GkCggtLlSvphs')
                listeners_text = listeners_span.text.strip()
                print(f"Found listeners text: {listeners_text} from {spotify_url}")

                listeners = int(listeners_text.split()[0].replace('.', '').replace(' ', ''))
                listeners_data[spotify_url] = listeners
            except Exception:
                print(f"Problem fetching data for {spotify_url}")
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
                print(f"Inserted {listeners} listeners for artist with ID {artist_id}")
            except Exception as e:
                print(f"Error inserting data: {e}")
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
        else:
            print(f"Invalid data type for listeners: {listeners}, expected int")

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