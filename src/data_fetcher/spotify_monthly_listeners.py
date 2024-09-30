from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class MonthlyListeners:
    def __init__(self, db_connector):
        self.db_connector = db_connector
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

    def fetch_listeners(self, spotify_url):
        self.driver.get(spotify_url)
        time.sleep(3)

        try:

            listeners_span = self.driver.find_element(By.CSS_SELECTOR, 'span.Ydwa1P5GkCggtLlSvphs')
            listeners_text = listeners_span.text.strip()
            print(f"Found listeners text: {listeners_text}")


            listeners = int(listeners_text.split()[0].replace('.', '').replace(' ', ''))
            return listeners

        except Exception as e:
            print(f"Error fetching listeners: {e}")
            return None

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
        cursor.execute("SELECT artist_id, spotify_id FROM artists WHERE spotify_id IS NOT NULL")
        artists = cursor.fetchall()

        for artist_id, spotify_id in artists:
            spotify_url = f"https://open.spotify.com/artist/{spotify_id}"
            listeners = self.fetch_listeners(spotify_url)
            if listeners is not None:
                self.save_to_db(artist_id, listeners)

        cursor.close()
        self.driver.quit()
