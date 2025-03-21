from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class YouTubeScraper:
    def __init__(self):
        self.driver = None  # Initialize driver as None

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

    def get_video_views(self, url):
        """Fetch video views from a YouTube URL."""
        if not self.driver:
            self.driver = self._setup_driver()  # Initialize driver only when needed

        try:
            self.driver.get(url)
            views = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="count"]/yt-view-count-renderer/span[1]'))
            ).text
            return int(views.replace(" views", "").replace(",", ""))
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error fetching views from {url}: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()  # Close the driver after fetching data
                self.driver = None

    def update_all_youtube_views(self, db):
        """Update YouTube views for all songs in the database."""
        songs = db.fetch_all("SELECT song_id, youtube_url, main_artist_id FROM songs WHERE youtube_url IS NOT NULL")
        artist_total_views = {}  # To store total views per artist

        for song in songs:
            song_id, youtube_url, artist_id = song
            views = self.get_video_views(youtube_url)
            if views:
                self.save_youtube_views_to_db(db, song_id, artist_id, views)
                print(f"Updated YouTube views for song ID {song_id}: {views} views")
                # Update the artist's total views
                if artist_id in artist_total_views:
                    artist_total_views[artist_id] += views
                else:
                    artist_total_views[artist_id] = views

        # Update media_kit_data with total YouTube views for each artist
        for artist_id, total_views in artist_total_views.items():
            self._update_media_kit_data(db, artist_id, total_views)

    @staticmethod
    def save_youtube_views_to_db(db, song_id, artist_id, views):
        """Save YouTube views to the database."""
        connection = db.connect()
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO youtube_song_countview (song_id, artist_id, countview)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (song_id, artist_id, views))
            connection.commit()
        except Exception as e:
            print(f"Error saving YouTube views for song ID {song_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def _update_media_kit_data(db, artist_id, total_views):
        """Update the total YouTube views for an artist in the media_kit_data table."""
        connection = db.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO media_kit_data (artist_id, youtube_views)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE youtube_views = %s
            """, (artist_id, total_views, total_views))
            connection.commit()
        except Exception as e:
            print(f"Error updating media_kit_data for artist ID {artist_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()