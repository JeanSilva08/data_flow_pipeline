class Artist:
    def __init__(self, **kwargs):
        self.artist_id = int(kwargs.get("artist_id")) if kwargs.get("artist_id") else None
        self.name = str(kwargs.get("name")) if kwargs.get("name") else None
        self.category = str(kwargs.get("category")) if kwargs.get("category") else None
        self.r_label = str(kwargs.get("r_label")) if kwargs.get("r_label") else None
        self.spotify_id = str(kwargs.get("spotify_id")) if kwargs.get("spotify_id") else None
        self.youtube_id = str(kwargs.get("youtube_id")) if kwargs.get("youtube_id") else None
        self.Instagram_id = str(kwargs.get("Instagram_id")) if kwargs.get("Instagram_id") else None
        self.TikTok_id = str(kwargs.get("TikTok_id")) if kwargs.get("TikTok_id") else None
        self.Twitter_id = str(kwargs.get("Twitter_id")) if kwargs.get("Twitter_id") else None
        self.Twitch_id = str(kwargs.get("Twitch_id")) if kwargs.get("Twitch_id") else None
        self.Spotify_url = str(kwargs.get("Spotify_url")) if kwargs.get("Spotify_url") else None
        self.youtube_url = str(kwargs.get("youtube_url")) if kwargs.get("youtube_url") else None
        self.instagram_url = str(kwargs.get("instagram_url")) if kwargs.get("instagram_url") else None
        self.tiktok_url = str(kwargs.get("tiktok_url")) if kwargs.get("tiktok_url") else None
        self.twitter_url = str(kwargs.get("twitter_url")) if kwargs.get("twitter_url") else None
        self.twitch_url = str(kwargs.get("twitch_url")) if kwargs.get("twitch_url") else None

    def save_to_db(self, db):
        try:
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
            self.artist_id = cursor.lastrowid
            db.connection.commit()
            return True
        except Exception as e:
            db.connection.rollback()
            print(f"Error saving artist: {e}")
            return False

    @staticmethod
    def update_in_db(db, artist_id, **kwargs):
        try:
            cursor = db.connection.cursor()
            set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
            query = f"UPDATE artists SET {set_clause} WHERE artist_id = %s"
            cursor.execute(query, (*kwargs.values(), artist_id))
            db.connection.commit()
            return True
        except Exception as e:
            db.connection.rollback()
            print(f"Error updating artist: {e}")
            return False

    @staticmethod
    def delete_from_db(db, artist_id):
        try:
            cursor = db.connection.cursor()
            query = "DELETE FROM artists WHERE artist_id = %s"
            cursor.execute(query, (artist_id,))
            db.connection.commit()
            return True
        except Exception as e:
            db.connection.rollback()
            print(f"Error deleting artist: {e}")
            return False

    @staticmethod
    def get_by_id(db, artist_id):
        try:
            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM artists WHERE artist_id = %s"
            cursor.execute(query, (artist_id,))
            result = cursor.fetchone()
            return Artist(**result) if result else None
        except Exception as e:
            print(f"Error fetching artist: {e}")
            return None

    @staticmethod
    def get_by_spotify_id(db, spotify_id):
        try:
            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM artists WHERE spotify_id = %s"
            cursor.execute(query, (spotify_id,))
            result = cursor.fetchone()
            return Artist(**result) if result else None
        except Exception as e:
            print(f"Error fetching artist by Spotify ID: {e}")
            return None

    @staticmethod
    def get_all(db, limit=None):
        try:
            cursor = db.connection.cursor(dictionary=True)
            query = "SELECT * FROM artists"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query)
            return [Artist(**row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching all artists: {e}")
            return []

    @staticmethod
    def exists(db, spotify_id=None, artist_id=None):
        if not spotify_id and not artist_id:
            return False

        try:
            cursor = db.connection.cursor()
            if spotify_id:
                query = "SELECT 1 FROM artists WHERE spotify_id = %s"
                cursor.execute(query, (spotify_id,))
            else:
                query = "SELECT 1 FROM artists WHERE artist_id = %s"
                cursor.execute(query, (artist_id,))
            return bool(cursor.fetchone())
        except Exception as e:
            print(f"Error checking artist existence: {e}")
            return False