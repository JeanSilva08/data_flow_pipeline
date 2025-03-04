class Artist:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.category = kwargs.get("category")
        self.r_label = kwargs.get("r_label")
        self.spotify_id = kwargs.get("spotify_id")
        self.youtube_id = kwargs.get("youtube_id")
        self.Instagram_id = kwargs.get("Instagram_id")
        self.TikTok_id = kwargs.get("TikTok_id")
        self.Twitter_id = kwargs.get("Twitter_id")
        self.Twitch_id = kwargs.get("Twitch_id")
        self.Spotify_url = kwargs.get("Spotify_url")
        self.youtube_url = kwargs.get("youtube_url")
        self.instagram_url = kwargs.get("instagram_url")
        self.tiktok_url = kwargs.get("tiktok_url")
        self.twitter_url = kwargs.get("twitter_url")
        self.twitch_url = kwargs.get("twitch_url")

    def save_to_db(self, db):
        cursor = db.connection.cursor()
        query = """
            INSERT INTO artists (
                name, category, r_label, spotify_id, youtube_id, Instagram_id,
                TikTok_id, Twitter_id, Twitch_id, Spotify_url, youtube_url,
                instagram_url, tiktok_url, twitter_url, twitch_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            self.name, self.category, self.r_label, self.spotify_id, self.youtube_id,
            self.Instagram_id, self.TikTok_id, self.Twitter_id, self.Twitch_id,
            self.Spotify_url, self.youtube_url, self.instagram_url, self.tiktok_url,
            self.twitter_url, self.twitch_url
        ))
        db.connection.commit()

    def update_in_db(self, db, artist_id):
        cursor = db.connection.cursor()
        query = """
            UPDATE artists SET
                name = %s, category = %s, r_label = %s, spotify_id = %s, youtube_id = %s,
                Instagram_id = %s, TikTok_id = %s, Twitter_id = %s, Twitch_id = %s,
                Spotify_url = %s, youtube_url = %s, instagram_url = %s, tiktok_url = %s,
                twitter_url = %s, twitch_url = %s
            WHERE artist_id = %s
        """
        cursor.execute(query, (
            self.name, self.category, self.r_label, self.spotify_id, self.youtube_id,
            self.Instagram_id, self.TikTok_id, self.Twitter_id, self.Twitch_id,
            self.Spotify_url, self.youtube_url, self.instagram_url, self.tiktok_url,
            self.twitter_url, self.twitch_url, artist_id
        ))
        db.connection.commit()

    @staticmethod
    def delete_from_db(db, artist_id):
        cursor = db.connection.cursor()
        query = "DELETE FROM artists WHERE artist_id = %s"
        cursor.execute(query, (artist_id,))
        db.connection.commit()

    @staticmethod
    def get_by_id(db, artist_id):
        cursor = db.connection.cursor()
        query = "SELECT * FROM artists WHERE artist_id = %s"
        cursor.execute(query, (artist_id,))
        return cursor.fetchone()

    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor()
        query = "SELECT * FROM artists"
        cursor.execute(query)
        return cursor.fetchall()