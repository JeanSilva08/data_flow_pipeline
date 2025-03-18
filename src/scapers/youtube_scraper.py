from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class YouTubeScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()  # Or any other driver you prefer

    def get_video_views(self, url):
        self.driver.get(url)
        try:
            views = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="count"]/yt-view-count-renderer/span[1]'))
            ).text
            return int(views.replace(" views", "").replace(",", ""))
        except (TimeoutException, NoSuchElementException) as e:
            print(f"Error fetching views from {url}: {e}")
            return None

    def update_all_youtube_views(self, db):
        songs = db.fetch_all("SELECT song_id, youtube_url, main_artist_id FROM songs WHERE youtube_url IS NOT NULL")
        for song in songs:
            song_id, youtube_url, artist_id = song
            views = self.get_video_views(youtube_url)
            if views:
                self.save_youtube_views_to_db(db, song_id, artist_id, views)
                print(f"Updated YouTube views for song ID {song_id}: {views} views")

    @staticmethod
    def save_youtube_views_to_db(db, song_id, artist_id, views):
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

    def close(self):
        self.driver.quit()