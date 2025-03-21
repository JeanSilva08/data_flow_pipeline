from src.scapers.youtube_scraper import YouTubeScraper  # Import the YouTubeScraper class

class YouTubeMusicScraper(YouTubeScraper):
    def update_all_youtubemsc_views(self, db):
        """Update YouTube Music views for all songs in the database."""
        songs = db.fetch_all("SELECT song_id, youtube_music_url, main_artist_id FROM songs WHERE youtube_music_url IS NOT NULL")
        artist_total_views = {}  # To store total views per artist

        for song in songs:
            song_id, youtube_music_url, artist_id = song
            views = self.get_video_views(youtube_music_url)
            if views:
                self.save_youtubemsc_views_to_db(db, song_id, artist_id, views)
                print(f"Updated YouTube Music views for song ID {song_id}: {views} views")
                # Update the artist's total views
                if artist_id in artist_total_views:
                    artist_total_views[artist_id] += views
                else:
                    artist_total_views[artist_id] = views

        # Update media_kit_data with total YouTube Music views for each artist
        for artist_id, total_views in artist_total_views.items():
            self._update_media_kit_data(db, artist_id, total_views)

    @staticmethod
    def save_youtubemsc_views_to_db(db, song_id, artist_id, views):
        """Save YouTube Music views to the database."""
        connection = db.connect()
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO youtubemsc_song_countview (song_id, artist_id, countview)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (song_id, artist_id, views))
            connection.commit()
        except Exception as e:
            print(f"Error saving YouTube Music views for song ID {song_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def _update_media_kit_data(db, artist_id, total_views):
        """Update the total YouTube Music views for an artist in the media_kit_data table."""
        connection = db.connect()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO media_kit_data (artist_id, youtube_music_views)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE youtube_music_views = %s
            """, (artist_id, total_views, total_views))
            connection.commit()
        except Exception as e:
            print(f"Error updating media_kit_data for artist ID {artist_id}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()