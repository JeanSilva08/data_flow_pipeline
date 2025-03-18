from googleapiclient.discovery import build  # Ensure this import is present

class YouTubeAPI:
    def __init__(self, api_key):
        """
        Initialize the YouTube API client with the provided API key.
        """
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=self.api_key)  # Explicitly use the API key

    def get_video_views(self, video_id):
        """
        Fetch the view count for a YouTube video using its video ID.
        """
        request = self.youtube.videos().list(part="statistics", id=video_id)
        response = request.execute()
        if response['items']:
            return int(response['items'][0]['statistics']['viewCount'])
        return 0

    def update_all_youtube_views(self, db):
        """
        Update the YouTube views for all songs in the database.
        """
        songs = db.fetch_all("SELECT song_id, youtube_id, main_artist_id FROM songs WHERE youtube_id IS NOT NULL")
        for song in songs:
            song_id, youtube_id, artist_id = song
            views = self.get_video_views(youtube_id)
            if views:
                self.save_youtube_views_to_db(db, song_id, artist_id, views)
                print(f"Updated YouTube views for song ID {song_id}: {views} views")

    @staticmethod
    def save_youtube_views_to_db(db, song_id, artist_id, views):
        """
        Save the YouTube views to the `youtube_song_countview` table.
        """
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