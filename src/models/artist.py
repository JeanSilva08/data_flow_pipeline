class Artist:
    def __init__(self, **kwargs):
        self.artist_id = kwargs.get("artist_id")  # Add this line
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

    @staticmethod
    def update_in_db(db, artist_id, **kwargs):
        """
        Update the artist data in the database.
        """
        cursor = db.connection.cursor()
        set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE artists SET {set_clause} WHERE artist_id = %s"
        cursor.execute(query, (*kwargs.values(), artist_id))
        db.connection.commit()

    @staticmethod
    def delete_from_db(db, artist_id):
        cursor = db.connection.cursor()
        query = "DELETE FROM artists WHERE artist_id = %s"
        cursor.execute(query, (artist_id,))
        db.connection.commit()

    @staticmethod
    def get_by_id(db, artist_id):
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM artists WHERE artist_id = %s"
        cursor.execute(query, (artist_id,))
        result = cursor.fetchone()
        if result:
            return Artist(**result)  # Ensure the Artist instance is created with all fields
        return None

    @staticmethod
    def get_by_spotify_id(db, spotify_id):
        """
        Fetch an artist by their Spotify ID.
        """
        cursor = db.connection.cursor(dictionary=True)
        query = "SELECT * FROM artists WHERE spotify_id = %s"
        cursor.execute(query, (spotify_id,))
        result = cursor.fetchone()
        if result:
            return Artist(**result)  # Ensure the Artist instance is created with all fields
        return None

    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor()
        query = "SELECT * FROM artists"
        cursor.execute(query)
        return cursor.fetchall()