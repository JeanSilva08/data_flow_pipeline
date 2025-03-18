from src.apis.youtube_api import YouTubeAPI

class YouTubeMusicAPI(YouTubeAPI):
    def update_all_youtubemsc_views(self, db):
        songs = db.fetch_all("SELECT song_id, ytmsc_id, main_artist_id FROM songs WHERE ytmsc_id IS NOT NULL")
        for song in songs:
            song_id, ytmsc_id, artist_id = song
            views = self.get_video_views(ytmsc_id)
            if views:
                self.save_youtubemsc_views_to_db(db, song_id, artist_id, views)
                print(f"Updated YouTube Music views for song ID {song_id}: {views} views")

    @staticmethod
    def save_youtubemsc_views_to_db(db, song_id, artist_id, views):
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