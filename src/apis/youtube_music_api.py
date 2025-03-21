from src.apis.youtube_api import YouTubeAPI

class YouTubeMusicAPI(YouTubeAPI):
    def update_all_youtubemsc_views(self, db):
        try:
            # Fetch all songs with valid YouTube Music IDs
            songs = db.fetch_all("SELECT song_id, ytmsc_id, main_artist_id FROM songs WHERE ytmsc_id IS NOT NULL")
            for song in songs:
                song_id, ytmsc_id, artist_id = song
                views = self.get_video_views(ytmsc_id)
                if views:
                    self.save_youtubemsc_views_to_db(db, song_id, artist_id, views)
                    print(f"Updated YouTube Music views for song ID {song_id}: {views} views")
        except Exception as e:
            print(f"Error updating YouTube Music views: {e}")
        finally:
            # Optionally close the connection if needed
            pass

    @staticmethod
    def save_youtubemsc_views_to_db(db, song_id, artist_id, views):
        connection = None
        cursor = None
        try:
            connection = db.connect()
            cursor = connection.cursor()
            query = """
                INSERT INTO youtubemsc_song_countview (song_id, artist_id, countview)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE countview = %s
            """
            cursor.execute(query, (song_id, artist_id, views, views))
            connection.commit()
            print(f"Saved YouTube Music views for song ID {song_id}.")
        except Exception as e:
            print(f"Error saving YouTube Music views for song ID {song_id}: {e}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()